from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth.decorators import login_required

from . import members_urls

urlpatterns = [
    url(r'^(?P<content_type_id>\d+)/(?P<object_id>\d+)/', include(members_urls)),
]
