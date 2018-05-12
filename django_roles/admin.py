from django.contrib import admin

from django.conf import settings

from .models import *


class ProjectUrlAdmin(admin.ModelAdmin):
    list_display = ('name', 'pattern')

    class Media:
        css = {
            'all': ('pretty.css',)
        }
        js = (
            'https://code.jquery.com/jquery-3.3.1.min.js',
            os.path.join(settings.STATIC_URL, "django_roles/js/project_url_actions.js"))


admin.site.register(RolePermission)
admin.site.register(Role)
admin.site.register(GenericMember)
admin.site.register(BulkInvitation)
admin.site.register(MembershipInvitation)
admin.site.register(ProjectUrl, ProjectUrlAdmin)
admin.site.register(UrlPermission)
