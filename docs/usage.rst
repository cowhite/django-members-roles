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

    {% url 'django-members-roles:manage-staff' content_type_id object_id %}

- This app adds the staff/members of the group to the model GenericMember that we have added. But if you want to have additional fields to the members, you can add a one to one model like this::

    from django_members_roles.models import GenericMember

    class MyOrganizationMembership(models.Model):
        generic_member = models.OneToOneField(GenericMember)
        additional_field = models.TextField()

How to use ?
------------

Invitation System Usage:
------------------------
After visiting the url 'django-members-roles:manage-staff', you will have options to see the members, add new member, see the roles and add new role. You can click "add member" to add a new member. And click "Member List" to see the list of members. You can invite multiple people at once.

Project Url:
------------



