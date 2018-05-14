from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from django_members_roles.models import DateTimeBase


class Organization(DateTimeBase):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)

    def __unicode__(self):
        return u'%s' % self.name

    @classmethod
    def get_content_type(cls):
        return ContentType.objects.get(app_label='app1', model='organization')
