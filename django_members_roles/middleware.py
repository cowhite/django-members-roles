from django.core.exceptions import PermissionDenied
from django.urls import resolve
from django.conf import settings
from . import app_settings
from django.contrib.contenttypes.models import ContentType


from .models import ProjectUrl, UrlPermissionRequired, GenericMember, has_url_permission


class UrlPermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        if not has_url_permission(request):
            raise PermissionDenied

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response