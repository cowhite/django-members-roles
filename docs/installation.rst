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

Middleware or decorator: You can add middleware or decorator for deciding whether a user can access a page or not. Add middleware if you want to check permissions for all urls of the project. Add decorator if you want to check permissions only for some of the urls.

Adding middleware::

    MIDDLEWARE = [
        # default other middlewares
        # ....
        'django_members_roles.middleware.url_permission_middleware',
    ]

Adding decorator::

    from .decorators import has_url_permission_decorator
    url(r'^$', has_url_permission_decorator(login_required(ExampleClassBasedView.as_view())),
        name="example-url"),

    url(r'^$', has_url_permission_decorator(login_required(example_function_based_view)),
        name="example-url"),

Optional settings in settings.py(more details in configuration)::

    DJANGO_MEMBERS_ROLES_CONFIRMATION_REQUIRED # Default is True
    DJANGO_MEMBERS_ROLES_TEST_CASE_MODEL_NAME # Default is "group"
    DJANGO_MEMBERS_ROLES_TEST_CASE_APP_LABEL # Default is "auth"
    DJANGO_MEMBERS_ROLES_QUERY_PARAM_CONTENT_TYPE_ID # Default is "content_type_id"
    DJANGO_MEMBERS_ROLES_QUERY_PARAM_OBJECT_ID # Default is "object_id"
    DJANGO_MEMBERS_ROLES_INVITATION_METHOD # Default is "cron"





