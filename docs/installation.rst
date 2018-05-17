Installation
============

Install latest version from pypi::

    pip install django-members-roles

Required settings in settings.py::

    # Add django_members_roles to INSTALLED_APPS
    INSTALLED_APPS = [
        #...
        django_members_roles,
        #...
    ]

Add to urls.py. Note that the exact namespacec of django-members-roles is mandatory::

    url(r'^django_members_roles/', include(
        'django_members_roles.urls', namespace='django-members-roles')),

Optional settings in settings.py(more details in configuration)::

    DJANGO_MEMBERS_ROLES_CONFIRMATION_REQUIRED # Default is True
    DJANGO_MEMBERS_ROLES_TEST_CASE_MODEL_NAME # Default is "group"
    DJANGO_MEMBERS_ROLES_TEST_CASE_APP_LABEL # Default is "auth"
    DJANGO_MEMBERS_ROLES_QUERY_PARAM_CONTENT_TYPE_ID # Default is "content_type_id"
    DJANGO_MEMBERS_ROLES_QUERY_PARAM_OBJECT_ID # Default is "object_id"
    DJANGO_MEMBERS_ROLES_INVITATION_METHOD # Default is "cron"





