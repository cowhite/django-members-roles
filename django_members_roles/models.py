from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib.sites.models import Site
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import Permission
from django.conf.urls import RegexURLPattern, RegexURLResolver
from django.core import urlresolvers
from django.urls import resolve
from . import app_settings

from .tasks import send_invitations_task

import os
import uuid


class DateTimeBase(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class RolePermission(DateTimeBase):
    content_type = models.ForeignKey(ContentType)
    permissions = models.ManyToManyField(Permission)


class Role(DateTimeBase):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    permissions = models.ManyToManyField(Permission)


class GenericMember(DateTimeBase):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    role = models.ForeignKey(Role, null=True, blank=True)


class BulkInvitation(DateTimeBase):
    emails = models.TextField()
    invited_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    invitations_sent = models.BooleanField(default=False)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')


class MembershipInvitation(DateTimeBase):
    code = models.UUIDField()
    email = models.EmailField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, related_name="membership_invitations")
    accepted_invitation = models.NullBooleanField()
    accepted_time = models.DateTimeField(null=True, blank=True)
    decline_time = models.DateTimeField(null=True, blank=True)
    decline_invitation = models.NullBooleanField()
    invalid_email = models.BooleanField(default=False)
    invitation_sent = models.BooleanField(default=False)
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="invited_membership_invitations")
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def save(self, *args, **kwargs):
        if not self.code:
            code = uuid.uuid1()

            while 1:
                try:
                    MembershipInvitation.objects.get(code=code)
                    code = uuid.uuid1()
                except MembershipInvitation.DoesNotExist:
                    break
            self.code = code
        super(MembershipInvitation, self).save(*args, **kwargs)

    def get_invitation_url(self):
        site_id = settings.SITE_ID
        site = Site.objects.get(id=site_id)
        membership_invitation_url = os.path.join(
            site.domain, reverse("django-members-roles:accept-decline-invitation", kwargs={"uu_id": self.code.hex})[1:])

        return membership_invitation_url


class ProjectUrl(DateTimeBase):
    pattern = models.TextField()
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return u"%s | %s" % (self.name, self.pattern)

    @classmethod
    def update_urls(cls):
        all_urls = []

        def fetch_urls(urls):
            for url in urls.url_patterns:
                if isinstance(url, RegexURLResolver):
                    fetch_urls(url)
                elif isinstance(url, RegexURLPattern):
                    all_urls.append(url)

        fetch_urls(urlresolvers.get_resolver())

        for url in all_urls:
            name = url.name
            if not name:
                continue
            pattern = url.regex.pattern
            try:
                obj = ProjectUrl.objects.get(name=name)
                obj.pattern = pattern
                obj.save()
            except ProjectUrl.DoesNotExist:
                ProjectUrl.objects.create(name=name, pattern=pattern)


class UrlPermissionRequired(DateTimeBase):
    url = models.ForeignKey(ProjectUrl)
    permissions = models.ManyToManyField(Permission)


@receiver(post_save, sender=BulkInvitation, dispatch_uid="create_invitation")
def create_invitation(sender, instance, **kwargs):
    if kwargs['created']:
        if instance.id and not instance.invitations_sent and \
            app_settings.DJANGO_MEMBERS_ROLES_INVITATION_METHOD == "celery":
            # Use cron to run the task as management command if DJANGO_MEMBERS_ROLES_INVITATION_METHOD is not celery
            send_invitations_task.delay(instance.id)
        elif instance.id and not instance.invitations_sent and \
            app_settings.DJANGO_MEMBERS_ROLES_INVITATION_METHOD == "direct":
            send_invitations_task(instance.id)


def send_invitations(self):
    if self.invitations_sent:
        return

    emails = self.emails.strip().split(",")
    for email in emails:
        email = email.replace("\r", "").replace("\n", "").strip()
        try:
            invitation = MembershipInvitation.objects.get(
                email=email, content_type=self.content_type,
                object_id=self.object_id, invited_by=self.invited_by)
            if invitation.invitation_sent:
                continue
        except MembershipInvitation.DoesNotExist:
            try:
                validate_email(email)
            except ValidationError:
                invitation = MembershipInvitation.objects.create(
                    content_type=self.content_type, object_id=self.object_id,
                    email=email, invited_by=self.invited_by,
                    invalid_email=True)
                continue
            try:
                user = User.objects.get(email=email)
                invitation = MembershipInvitation.objects.create(
                    content_type=self.content_type, object_id=self.object_id,
                    email=email, user=user, invited_by=self.invited_by)
            except User.DoesNotExist:
                invitation = MembershipInvitation.objects.create(
                    content_type=self.content_type, object_id=self.object_id,
                    email=email, invited_by=self.invited_by)

        invitation_url = invitation.get_invitation_url()
        invited_by = self.invited_by
        subject = render_to_string(
            "django_members_roles/mails/membership_invitation_subject.html",
            {"invited_by": invited_by.username, "invitation": invitation})
        body = render_to_string(
            "django_members_roles/mails/membership_invitation.html",
            {"invited_by": invited_by, "invitation_url": invitation_url, "invitation": invitation})
        send_mail(
            subject, '', settings.DEFAULT_FROM_EMAIL, [email],
            html_message=body)
        invitation.invitation_sent = True
        invitation.save()
    self.invitations_sent = True
    self.save()


def permission_str_method(self):
    return "%s | %s" % (
        self.content_type,
        self.name)

def has_url_permission(request):
    current_user = request.user
    url_name = resolve(request.path_info).url_name
    try:
        project_url_obj = ProjectUrl.objects.get(name=url_name)
        try:
            url_permission_required_obj = UrlPermissionRequired.objects.get(url=project_url_obj)

            if url_permission_required_obj.permissions.count() > 0:
                content_type_id_query = app_settings.DJANGO_MEMBERS_ROLES_QUERY_PARAM_CONTENT_TYPE_ID
                object_id_query = app_settings.DJANGO_MEMBERS_ROLES_QUERY_PARAM_OBJECT_ID

                content_type_id = request.GET.get(content_type_id_query, None)
                object_id = request.GET.get(object_id_query, None)
                content_object = None

                content_type = None

                if not content_type_id or not object_id:
                    return False

                try:
                    content_type = ContentType.objects.get(id=content_type_id)
                except ContentType.DoesNotExist:
                    return False

                model_class = content_type.model_class()

                try:
                    content_object = model_class.objects.get(id=object_id)
                except model_class.DoesNotExist:
                    return False

                try:
                    generic_member = GenericMember.objects.get(
                        content_type_id=content_type_id, object_id=object_id,
                        user=current_user)
                except GenericMember.DoesNotExist:
                    return False

                try:
                    admin_role = Role.objects.get(
                        name="admin", content_type_id=content_type_id,
                        object_id= object_id)
                    if admin_role in generic_member.role.permissions.all():
                        return True
                except Role.DoesNotExist:
                    pass
                if generic_member.role:
                    current_user_permissions = generic_member.role.permissions.all()

                    for required_permission in url_permission_required_obj.permissions.all():
                        if required_permission not in current_user_permissions:
                            return False
                else:
                    return False

        except UrlPermissionRequired.DoesNotExist:
            pass
    except ProjectUrl.DoesNotExist:
        pass
    return True

def create_admin_role(content_object, user):
    content_type = ContentType.objects.get_for_model(content_object)
    object_id = content_object.id

    try:
        generic_member = GenericMember.objects.get(
            user=user, content_type= content_type, object_id= object_id)
    except GenericMember.DoesNotExist:
        generic_member = GenericMember.objects.create(
            user= user, content_type= content_type, object_id= object_id,
            )
    try:
        role = Role.objects.get(
            content_type= content_type, object_id=object_id,
            name= "admin")
    except Role.DoesNotExist:
        role = Role.objects.create(
            content_type= content_type, object_id= object_id,
            name = "admin"
        )

    generic_member.role = role
    generic_member.save()


BulkInvitation.add_to_class('send_invitations', send_invitations)

Permission.add_to_class('__str__', permission_str_method)
