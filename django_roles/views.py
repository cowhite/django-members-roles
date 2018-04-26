from django.shortcuts import render

from django.contrib.contenttypes.models import ContentType
from django.views import generic as generic_views
from django.conf import settings
from django.contrib.auth.models import User

from .models import *
from .forms import *
from . import app_settings


class ManageStaffFullView(generic_views.TemplateView):
    template_name = "django_roles/full_view.html"

    def get_context_data(self, *args, **kwargs):
        context = super(ManageStaffFullView,
                        self).get_context_data(*args, **kwargs)
        context['object_id'] = self.kwargs['object_id']
        context['content_type_id'] = self.kwargs['content_type_id']
        context['content_type'] = ContentType.objects.get(
            id=self.kwargs['content_type_id'])
        return context


class AddStaffView(generic_views.FormView):
    template_name = "django_roles/forms/add_members.html"
    form_class = BulkInvitationForm

    def form_valid(self, form):
        user = self.request.user
        content_type = ContentType.objects.get(
            id=self.kwargs['content_type_id'])
        object_id = self.kwargs['object_id']
        instance = form.save(
            user=self.request.user, content_type=content_type, object_id=object_id)
        return JsonResponse({"message": "success"})

    def form_invalid(self, form):
        res = super(AddStaffView, self).form_invalid(form)
        res.render()
        return JsonResponse({"error": True, "html": res.content})


class StaffListView(generic_views.TemplateView):
    template_name = "django_roles/list/staff_members.html"

    def get_context_data(self, *args, **kwargs):
        context = super(StaffListView,
                        self).get_context_data(*args, **kwargs)
        content_type = ContentType.objects.get(
            id=self.kwargs['content_type_id'])
        object_id = self.kwargs['object_id']
        confirmation_required = app_settings.DJANGO_ROLES_CONFIRMATION_REQUIRED
        if not confirmation_required:
            invitations = list(MembershipInvitation.objects.filter(
                content_type=content_type,
                object_id=object_id).values_list("user_id", flat=True))
        else:
            invitations = list(MembershipInvitation.objects.filter(
                content_type=content_type,
                object_id=object_id,
                accepted_invitation=True).values_list("user_id", flat=True))

        users = User.objects.filter(id__in=invitations)

        context['staff'] = users
        return context
