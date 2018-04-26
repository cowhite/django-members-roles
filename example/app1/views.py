from django.shortcuts import render, get_object_or_404, render_to_response, redirect
from django.views.generic import FormView, TemplateView, UpdateView, DeleteView, View
from django.http import JsonResponse

from .models import Organization
from .forms import OrganizationForm


class OrganizationCreateView(FormView):
    template_name = "app1/organizations/forms/organization.html"
    form_class = OrganizationForm

    def form_valid(self, form):
        instance = form.save(user=self.request.user)
        return JsonResponse({"message": "success"})

    def form_invalid(self, form):
        res = super(JobCreateView, self).form_invalid(form)
        res.render()
        return JsonResponse({"error": True, "html": res.content})


class OrganizationFullView(TemplateView):
    template_name = "app1/organizations/full_view.html"


class OrganizationsListView(TemplateView):
    template_name = "app1/organizations/list/organizations.html"

    def get_context_data(self, *args, **kwargs):
        context = super(OrganizationsListView,
                        self).get_context_data(*args, **kwargs)
        organizations = Organization.objects.all()
        context['organizations'] = organizations
        return context
