from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth.decorators import login_required

from . import members_urls
from .views import *

urlpatterns = [
    url(r'^(?P<content_type_id>\d+)/(?P<object_id>\d+)/', include(members_urls)),
    url(r'^invitation_process/(?P<uu_id>[^/]+)/$', login_required(AcceptDeclineInvitationView.as_view()),
        name="accept-decline-invitation"),
    url(r'^messages/$', message_view, name="messages"),
]
