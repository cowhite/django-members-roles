from django.core.exceptions import PermissionDenied
from django.urls import resolve
from django.conf import settings
from . import app_settings
from django.contrib.contenttypes.models import ContentType


from .models import ProjectUrl, UrlPermissionRequired, GenericMember, has_url_permission


def url_permission_middleware(get_response):
    # One-time configuration and initialization.

    def middleware(request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        if not has_url_permission(request):
            raise PermissionDenied

        response = get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    return middleware