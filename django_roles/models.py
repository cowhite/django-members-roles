from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.conf import settings


class DateTimeBase(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Role(DateTimeBase):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)


class GenericMember(DateTimeBase):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    role = models.ForeignKey(Role, null=True, blank=True)


class BulkInvitation(DateTimeBase):
    emails = models.TextField()
    invited_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')


class MembershipInvitation(DateTimeBase):
    code = models.UUIDField()
    email = models.EmailField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, related_name="membership_invitations")
    accepted_invitation = models.BooleanField(default=False)
    accepted_time = models.DateTimeField(null=True, blank=True)
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="invited_membership_invitations")
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
