from django.shortcuts import render, redirect, get_object_or_404

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
    template_name = "django_members_roles/full_view.html"

    def get_context_data(self, *args, **kwargs):
        context = super(ManageStaffFullView,
                        self).get_context_data(*args, **kwargs)
        context['object_id'] = self.kwargs['object_id']
        context['content_type_id'] = self.kwargs['content_type_id']
        context['content_type'] = ContentType.objects.get(
            id=self.kwargs['content_type_id'])
        return context


class AddStaffView(generic_views.FormView):
    template_name = "django_members_roles/forms/add_members.html"
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


class CreatAndUpdateRoleView(generic_views.FormView):
    template_name = "django_members_roles/forms/add_role.html"
    form_class = RoleForm

    def get_form_kwargs(self):
        kwargs = super(CreatAndUpdateRoleView, self).get_form_kwargs()
        kwargs['content_type_id'] = self.kwargs['content_type_id']
        return kwargs

    def get_form(self, form_class=None):
        try:
            role_id = self.request.GET.get('role_id', None)
            if role_id:
                role = Role.objects.get(id=role_id)
                return self.form_class(instance=role, **self.get_form_kwargs())
            else:
                return self.form_class(**self.get_form_kwargs())
        except Role.DoesNotExist:
            return self.form_class(**self.get_form_kwargs())

    def form_valid(self, form):
        content_type = ContentType.objects.get(
            id=self.kwargs['content_type_id'])
        object_id = self.kwargs['object_id']
        instance = form.save(content_type=content_type, object_id=object_id)
        form.save_m2m()
        return JsonResponse({"message": "success"})

    def form_invalid(self, form):
        res = super(CreatAndUpdateRoleView, self).form_invalid(form)
        html = render_to_string(self.template_name, {"form": form})
        print(html)
        return JsonResponse({"error": True, "html": html})


class RoleListView(generic_views.TemplateView):
    template_name = "django_members_roles/list/roles.html"

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


class DeleteRoleView(generic_views.DeleteView):
    model = Role

    def get_object(self, *args, **kwargs):
        return get_object_or_404(Role, id=self.kwargs['pk'])

    def get_success_url(self, *args, **kwargs):
        content_type_id = self.kwargs['content_type_id']
        object_id = self.kwargs['object_id']
        return reverse("django-members-roles:role-list",
                       kwargs={"content_type_id": content_type_id,
                               "object_id": object_id})


class StaffListView(generic_views.TemplateView):
    template_name = "django_members_roles/list/staff_members.html"

    def get_context_data(self, *args, **kwargs):
        context = super(StaffListView,
                        self).get_context_data(*args, **kwargs)
        content_type = ContentType.objects.get(
            id=self.kwargs['content_type_id'])
        object_id = self.kwargs['object_id']
        roles = Role.objects.filter(
            content_type=content_type, object_id=object_id)
        invitations = MembershipInvitation.objects.filter(
            content_type=content_type,
            object_id=object_id,
            accepted_invitation=True)
        invitations_list = list(
            invitations.values_list("user_id", flat=True))

        users = User.objects.filter(id__in=invitations_list)
        generic_members = GenericMember.objects.filter(
            user_id__in=invitations_list, content_type=content_type,
            object_id = object_id)
        context['staff'] = generic_members
        context['roles'] = roles
        return context


class AcceptDeclineInvitationView(generic_views.View):

    def get(self, request, * args, **kwargs):
        uu_id = kwargs['uu_id']
        invitation = None
        try:
            invitation = MembershipInvitation.objects.get(
                code=uu_id, email=self.request.user.email)
        except MembershipInvitation.DoesNotExist:
            return redirect("%s?msg=You don't have permission to accept this invitation" % reverse('django-members-roles:messages'))
        return render(request, "django_members_roles/includes/accept_decline_invitation.html",
                      {"uu_id": uu_id, "invitation": invitation})

    def post(self, request, *args, **kwargs):
        uu_id = kwargs['uu_id']
        accept_status = self.request.POST.get("accept_status", None)
        user = self.request.user
        if uu_id:
            try:
                invitation = MembershipInvitation.objects.get(code=uu_id,
                                                              email=user.email)
                print(invitation.content_type_id)
                print(invitation.object_id)
                if accept_status == "True":
                    invitation.accepted_invitation = True
                    invitation.accepted_time = timezone.now()
                    GenericMember.objects.get_or_create(
                        content_type=invitation.content_type,
                        object_id=invitation.object_id, user=user)
                elif accept_status == "False":
                    invitation.decline_invitation = True
                    invitation.decline_time = timezone.now()
                else:
                    pass
                invitation.user = user
                invitation.save()
            except MembershipInvitation.DoesNotExist:
                return redirect("%s?msg=You don't have permission to accept this invitation" % reverse('django-members-roles:messages'))
            if accept_status =="True":
                return redirect("%s?msg=Thank you for accepting this invitation" % reverse('django-members-roles:messages'))
            elif accept_status == "False":
                return redirect("%s?msg=You declined this invitation" % reverse('django-members-roles:messages'))
            else:
                return redirect("%s?msg=Somthing went wrong please contact admin" % reverse('django-members-roles:messages'))
        else:
            return redirect("%s?msg=You don't have permission to accept this invitation" %reverse('django-members-roles:messages'))


def message_view(request):
    msg = request.GET['msg']
    return render(request, 'django_members_roles/includes/invitation_response_message.html', {"msg": msg})


class UpdateRoletoMemeber(generic_views.View):

    def post(self, request, *args, **kwargs):
        role_id = self.request.POST.get("role_id", None)
        user_id = self.request.POST.get("user_id", None)
        content_type = ContentType.objects.get(
            id=self.kwargs['content_type_id'])
        object_id = self.kwargs['object_id']
        if role_id:
            staff_memeber = get_object_or_404(GenericMember,
                                              content_type=content_type, object_id=object_id, user_id=user_id)
            if role_id == "null":
                staff_memeber.role = None
            else:
                role = get_object_or_404(Role, id=role_id)
                staff_memeber.role = role
            staff_memeber.save()
            return JsonResponse({"message": "success"})
        else:
            return JsonResponse({"error": True, "message": "required role id"})


class UpdateProjectUrlsView(generic_views.View):
    def post(self, request, *args, **kwargs):
        ProjectUrl.update_urls()
        return redirect(reverse("admin:django_members_roles_projecturl_changelist"))




