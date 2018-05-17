from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth.decorators import login_required

from .views import *
from .decorators import has_url_permission_decorator

urlpatterns = [
    url(r'^$', login_required(ManageStaffFullView.as_view()),
        name="manage-members"),
    url(r'^add_member/$', login_required(AddStaffView.as_view()),
        name="add-member"),
    url(r'^member_list/$', login_required(StaffListView.as_view()),
        name="member-list"),
    url(r'^create_and_update_role/$',
        login_required(CreatAndUpdateRoleView.as_view()), name="create-and-update-role"),
    url(r'^role_list/$', login_required(RoleListView.as_view()), name="role-list"),
    url(r'^update_member_role/$',
        login_required(UpdateRoletoMemeber.as_view()), name="update-member-role"),
    url(r'^delete_role/(?P<pk>\d+)/$',
        login_required(DeleteRoleView.as_view()), name="delete-role"),

]
