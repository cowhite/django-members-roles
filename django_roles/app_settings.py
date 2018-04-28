from django.conf import settings

DJANGO_ROLES_CONFIRMATION_REQUIRED = getattr(
    settings, 'DJANGO_ROLES_CONFIRMATION_REQUIRED', True)
