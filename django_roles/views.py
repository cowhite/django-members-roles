from django.shortcuts import render, redirect

from django.contrib.contenttypes.models import ContentType
from django.views import generic as generic_views
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.http import JsonResponse
from django.template.loader import render_to_string

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
        html = render_to_string(self.template_name, {"form": form})
        return JsonResponse({"error": True, "html": html})


class AddRoleView(generic_views.FormView):
    template_name = "django_roles/forms/add_role.html"
    form_class = RoleForm

    def form_valid(self, form):
        content_type = ContentType.objects.get(
            id=self.kwargs['content_type_id'])
        object_id = self.kwargs['object_id']
        instance = form.save(content_type=content_type, object_id=object_id)
        return JsonResponse({"message": "success"})

    def form_invalid(self, form):
        res = super(AddRoleView, self).form_invalid(form)
        html = render_to_string(self.template_name, {"form": form})
        return JsonResponse({"error": True, "html": html})


class RoleListView(generic_views.TemplateView):
    template_name = "django_roles/list/roles.html"

    def get_context_data(self, *args, **kwargs):
        context = super(RoleListView,
                        self).get_context_data(*args, **kwargs)
        content_type = ContentType.objects.get(
            id=self.kwargs['content_type_id'])
        object_id = self.kwargs['object_id']
        roles = Role.objects.filter(
            content_type=content_type, object_id=object_id)
        context['roles'] = roles
        return context


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
                object_id=object_id).exclude(decline_invitation=True).values_list("user_id", flat=True))
        else:
            invitations = list(MembershipInvitation.objects.filter(
                content_type=content_type,
                object_id=object_id,
                accepted_invitation=True).values_list("user_id", flat=True))

        users = User.objects.filter(id__in=invitations)

        context['staff'] = users
        return context


class AcceptDeclineInvitationView(generic_views.View):

    def get(self, request, * args, **kwargs):
        uu_id = kwargs['uu_id']
        invitation = None
        try:
            invitation = MembershipInvitation.objects.get(
                code=uu_id, email=self.request.user.email)
        except MembershipInvitation.DoesNotExist:
            return redirect("%s?msg=You don't have permission to accept this invitation" % reverse('messages'))
        return render(request, "django_roles/includes/accept_decline_invitation.html",
                      {"uu_id": uu_id, "invitation": invitation})

    def post(self, request, *args, **kwargs):
        uu_id = self.request.POST.get("uu_id", None)
        accept_status = self.request.POST.get("accept_status", None)
        user = self.request.user
        if uu_id:
            try:
                invitation = MembershipInvitation.objects.get(code=uu_id,
                                                              email=user.email)
                if accept_status:
                    invitation.accepted_invitation = True
                    invitation.accepted_time = timezone.now()

                else:
                    invitation.decline_invitation = True
                    invitation.decline_time = timezone.now()
                invitation.user = user
                invitation.save()
            except MembershipInvitation.DoesNotExist:
                return redirect("%s?msg=You don't have permission to accept this invitation" % reverse('messages'))
            if accept_status:
                return redirect("%s?msg=Thank you for accepting this invitation" % reverse('messages'))
            else:
                return redirect("%s?msg=You declined this invitation" % reverse('messages'))


def message_view(request):
    msg = request.GET['msg']
    return render(request, 'django_roles/includes/invitation_response_message.html', {"msg": msg})
