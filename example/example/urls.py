"""example URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth.decorators import login_required

from app1.views import *


urlpatterns = [
    url(r'^admin/', admin.site.urls),

    # Allauth
    url(r'^accounts/', include('allauth.urls')),

    # Mount django_members_roles
    url(r'^django_members_roles/', include('django_members_roles.urls', namespace='django-members-roles')),
    url(r'^organizations/$', login_required(OrganizationFullView.as_view()),
        name="organizations"),
    url(r'^new_organization/$', login_required(OrganizationCreateView.as_view()),
        name="new-organization"),
    url(r'^organizations_list/$', login_required(OrganizationsListView.as_view()),
        name="organizations-list"),
]
