Usage
=====

After doing initial setup mentioned in installation page, you need to know how to use this app.

What this app does ?
--------------------

- Allows a group(an organization or a college for example) to invite members to its group.
- Members need to accept the invitation to be part of the group.
- Allows customization of access to pages in the project based on roles.

Things to be done by the developer:
-----------------------------------

- Whenever a new group(an organization for example) is created, then an admin need to be added to that group as the first member with role 'admin'. For doing that, you need to call the function 'create_admin_role' with parameters 'content_object', 'user' after the group is created(you can do it either by overriding save method of that group or by catching a post_save signal)::

    class Organization(models.Model): # Organization is a kind of group
        my_field_for_user_who_created_this_org = models.ForeignKey(User)

        #...some fields...

        def save(self, *args, **kwargs):
            new_instance = False
            if self.id:
                new_instance = True
            super(Organization, self).save(*args, **kwargs)
            if new_instance:
                create_admin_role(self, self.my_field_for_user_who_created_this_org)

Or, you can do it using post_save signal::

    from django.db.models.signals import post_save
    from django.dispatch import receiver

    @receiver(post_save, sender=Organization, dispatch_uid="create_admin_role_for_organization")
    def create_admin_role_for_organization(sender, instance, **kwargs):
        if kwargs['created']:
            create_admin_role(instance, instance.my_field_for_user_who_created_this_org)

- In the group page(or whereever you want), place the link to manage staff. This is the link where we have done all the invitation system, role adding etc. Dont forget the namespace.::

    {% url 'django-members-roles:manage-members' content_type_id object_id %}

- This app adds the staff/members of the group to the model GenericMember that we have added. But if you want to have additional fields to the members, you can add a one to one model like this::

    from django_members_roles.models import GenericMember

    class MyOrganizationMembership(models.Model):
        generic_member = models.OneToOneField(GenericMember)
        additional_field = models.TextField()

- For every url that you want to check whether the current user has the permissions, you need to send the query parameters to that url like this::

    <a href="{% url 'abc' %}?content_type_id=12&object_id=1">Some link</a>

    Where the strings content_type_id and object_id can be changed by changing the settings DJANGO_MEMBERS_ROLES_QUERY_PARAM_CONTENT_TYPE_ID and DJANGO_MEMBERS_ROLES_QUERY_PARAM_OBJECT_ID.

    For example, if you set them as "cti" and "oi" in settings

    DJANGO_MEMBERS_ROLES_QUERY_PARAM_CONTENT_TYPE_ID = "cti"
    DJANGO_MEMBERS_ROLES_QUERY_PARAM_OBJECT_ID = "oi"

    then, you can send the url like

    <a href="{% url 'abc' %}?cti=12&oi=1">Some link</a>

    Here content_type_id is the content type id of the group(for example Organization) and object_id is the id of the instance of that Organization.

    Only this way, the middleware(or the decorator) that we developed will check the current user for permissions.

How to use ?
------------

Invitation System Usage:
------------------------
After visiting the url 'django-members-roles:manage-members', you will have options to see the members, add new member, see the roles and add new role. You can click "add member" to add a new member. And click "Member List" to see the list of members. You can invite multiple people at once.

Project Url:
------------
Go to the admin url '/admin/django_members_roles/projecturl/' and then click the button on the top right 'update project urls' which will take few seconds or minutes to update the list of project urls from your project.

Url Permission:
---------------
Add a new url permission at /admin/django_members_roles/urlpermissionrequired/add/ by selecting respective project url and necessary permissions required for that url. When checking, we will check whether the role belonging to the currently logged in user(for that content type) has all the permissions mentioned for this url. If atleast one permission is not present for that role of the currently logged in user(for that content type) then it will return 403 Permission Denied. All this happens with the help of a decorator or middleware that we developed.

Role Permission:
----------------
This might be little confusing so handle with little care. This model has two fields, one is content_type and the other is permissions. This must be added only in the admin. The developer need to decide the permissions that a group member can add to the roles for a group. As you know, a single project will have lots of permissions for many models. When the admin of the group is adding the permissions for a role, we should show only few options in the dropdown rather than all. So, the developer need to decide what are the permissions that may be required for a content type(or a group) and then add all those permissions to the content type in this role permission model.

Role:
-----
When adding/editing a role in the interface we developed at 'django-members-roles:manage-members', you can add all the permissions for that role. You can only pick some of the permissions here, not all. The list permissions in the dropdown shown here is dependant on the permissions enabled for a content type(that we added in RolePermission model).




