from django.contrib import admin

from django.conf import settings

from .models import *

import os


class ProjectUrlAdmin(admin.ModelAdmin):
    list_display = ('name', 'pattern')

    class Media:

        js = (
            'https://code.jquery.com/jquery-3.3.1.min.js',
            os.path.join(settings.STATIC_URL, "django_members_roles/js/project_url_actions.js"))


class Select2InAdmin(object):
    class Media:
        css = {
            'all': ('https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.5/css/select2.min.css',)
        }
        js = (
            'https://code.jquery.com/jquery-3.3.1.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.5/js/select2.min.js',
            os.path.join(settings.STATIC_URL, "django_members_roles/js/url_permission_required.js"),
        )

class UrlPermissionRequiredAdmin(admin.ModelAdmin, Select2InAdmin):
    pass

class RolePermissionAdmin(admin.ModelAdmin, Select2InAdmin):
    pass


admin.site.register(RolePermission, RolePermissionAdmin)
admin.site.register(Role)
admin.site.register(GenericMember)
admin.site.register(BulkInvitation)
admin.site.register(MembershipInvitation)
admin.site.register(ProjectUrl, ProjectUrlAdmin)
admin.site.register(UrlPermissionRequired, UrlPermissionRequiredAdmin)
