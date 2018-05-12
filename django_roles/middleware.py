from django.core.exceptions import PermissionDenied
from django.urls import resolve
from django.conf import settings
from django_roles import app_settings
from django.contrib.contenttypes.models import ContentType


from .models import ProjectUrl, UrlPermissionRequired, GenericMember


class UrlPermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        current_user = request.user
        url_name = resolve(request.path_info).url_name
        try:
            project_url_obj = ProjectUrl.objects.get(name=url_name)
            try:
                url_permission_required_obj = UrlPermissionRequired.objects.get(url=project_url_obj)

                if url_permission_required_obj.permissions.count() > 0:
                    content_type_id_query = app_settings.DJANGO_ROLES_QUERY_PARAM_CONTENT_TYPE_ID
                    object_id_query = app_settings.DJANGO_ROLES_QUERY_PARAM_OBJECT_ID

                    content_type_id = request.GET.get(content_type_id_query, None)
                    object_id = request.GET.get(object_id_query, None)
                    content_object = None

                    content_type = None

                    if not content_type_id or not object_id:
                        raise PermissionDenied

                    try:
                        content_type = ContentType.objects.get(id=content_type_id)
                    except ContentType.DoesNotExist:
                        raise PermissionDenied

                    model_class = content_type.model_class()

                    try:
                        content_object = model_class.objects.get(id=object_id)
                    except model_class.DoesNotExist:
                        raise PermissionDenied

                    try:
                        generic_member = GenericMember.objects.get(
                            content_type_id=content_type_id, object_id=object_id,
                            user=current_user)
                    except GenericMember.DoesNotExist:
                        raise PermissionDenied

                    current_user_permissions = generic_member.role.permissions.all()

                    for required_permission in url_permission_required_obj.permissions.all():
                        if required_permission not in current_user_permissions:
                            raise PermissionDenied

            except UrlPermissionRequired.DoesNotExist:
                pass
        except ProjectUrl.DoesNotExist:
            pass

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response