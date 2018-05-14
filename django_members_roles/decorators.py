from django.core.exceptions import PermissionDenied

from .models import has_url_permission

def has_url_permission_decorator(function):
    def wrap(request, *args, **kwargs):
        if has_url_permission(request):
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap