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
            site.domain, reverse("accept-decline-invitation", kwargs={"uu_id": self.code.hex})[1:])

        return membership_invitation_url


@receiver(post_save, sender=BulkInvitation, dispatch_uid="create_invitation")
def create_invitation(sender, instance, **kwargs):
    if kwargs['created']:
        if instance.id and not instance.invitations_sent and settings.INVITATION_METHOD == "celery":
            send_invitations_task.delay(instance.id)


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
            "django_roles/mails/membership_invitation_subject.html",
            {"invited_by": invited_by.username, "invitation": invitation})
        body = render_to_string(
            "django_roles/mails/membership_invitation.html",
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

BulkInvitation.add_to_class('send_invitations', send_invitations)

Permission.add_to_class('__str__', permission_str_method)
