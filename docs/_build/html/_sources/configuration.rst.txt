Configuration
=============

Optional settings in settings.py:

DJANGO_MEMBERS_ROLES_CONFIRMATION_REQUIRED

    Default: True

    Allowed values: True/False

    If True:

        A person who is invited to a group, needs to accept invitation before being a member of that group.

    If False:

        A person who is invited to a group, will be a member of the group even without accepting the invitation

DJANGO_MEMBERS_ROLES_QUERY_PARAM_CONTENT_TYPE_ID and DJANGO_MEMBERS_ROLES_QUERY_PARAM_OBJECT_ID

    Default for DJANGO_MEMBERS_ROLES_QUERY_PARAM_CONTENT_TYPE_ID: content_type_id # You can give anything like abc

    Default for DJANGO_MEMBERS_ROLES_QUERY_PARAM_OBJECT_ID: is "object_id" # You can give anything like def

    For every request that needs permission validation based on this app, it expects two query parameters(Or GET parameters). One if the value based on the setting DJANGO_MEMBERS_ROLES_QUERY_PARAM_CONTENT_TYPE_ID and the other is the value based on the setting DJANGO_MEMBERS_ROLES_QUERY_PARAM_OBJECT_ID.

    This app retrieves the content object using the above two settings and then it will see if the currently logged in user is a member of that content object. Then, it will fetch the role from the member and check the permissions added to that role and decides whether the current page can be viewed by the current user or not.


DJANGO_MEMBERS_ROLES_INVITATION_METHOD

    Default: cron

    Allowed values:

        celery # Preferred
        cron
        direct

    Celery:

    If the setting value is "celery" then we use celery for background tasks. That is, when someone invites people to a content object(or simply a group like Organization) then the invitation(s) will be sent to the people invited using celery(background process).

    Cron:

    We have provided a management command that you can add in cron so the invitations will be sent.

    Direct:

    We dont suggest this but you can use this. Direct means, the invitations to all the people invited will be sent in the request response cycle and not in the background process. This will affect the performance of the application. Please dont set it to "direct".


DJANGO_MEMBERS_ROLES_TEST_CASE_MODEL_NAME and DJANGO_MEMBERS_ROLES_TEST_CASE_APP_LABEL

    Note: Mostly not useful to you, so you can ignore this setting :)

    Default for DJANGO_MEMBERS_ROLES_TEST_CASE_MODEL_NAME: group
    Default for DJANGO_MEMBERS_ROLES_TEST_CASE_APP_LABEL: auth

    When the test cases are executed, we need a content object(or a model instance) which the tests treat as a group to add members to it. It can be any content object. And the content type and object id belonging to the content object will be based on the values provided for DJANGO_MEMBERS_ROLES_TEST_CASE_MODEL_NAME and DJANGO_MEMBERS_ROLES_TEST_CASE_APP_LABEL.
