from django.test import TestCase

from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.contrib.auth.models import Permission

from django_members_roles.models import (GenericMember, BulkInvitation,\
 Role, RolePermission, MembershipInvitation, UrlPermissionRequired, ProjectUrl)
from . import app_settings

import time
import uuid

class Common(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(
            username= "user1", password= "a",
            email= "user1@example.com")
        self.user1.is_staff= True
        self.user1.save()

        self.user2 = User.objects.create_user(
            username= "user2", password= "a",
            email= "user2@example.com")
        self.user2.is_superuser= True
        self.user2.save()

        self.group1 = Group.objects.create(name="group1")
        self.group2 = Group.objects.create(name="group2")

        self.content_type_obj = ContentType.objects.get(
            model= app_settings.DJANGO_MEMBERS_ROLES_TEST_CASE_MODEL_NAME,
            app_label= app_settings.DJANGO_MEMBERS_ROLES_TEST_CASE_APP_LABEL)

        permissions = Permission.objects.filter(content_type=self.content_type_obj)
        self.role_permission_obj = RolePermission.objects.create(
            content_type=self.content_type_obj)
        for permission in permissions:
            self.role_permission_obj.permissions.add(permission.id)

class GenericMemberFullViewTestCase(Common):

    def test_staff_full_view(self):
        self.client.login(username= self.user1, password= "a")
        res = self.client.get(reverse("django-members-roles:manage-members",
            kwargs={"content_type_id":self.content_type_obj.id,\
            "object_id":self.group1.id}))
        self.assertEqual(res.context['object_id'], str(self.group1.id))
        self.assertEqual(res.context['content_type_id'], str(self.content_type_obj.id))


class GenericMemberTestCase(Common):

    def test_sending_invitation(self):
        self.client.login(username=self.user1, password="a")
        emails = "user4@example.com,user5@example.com,user6@example.com"
        res = self.client.post(reverse("django-members-roles:add-member",
            kwargs={"content_type_id":self.content_type_obj.id,\
            "object_id":self.group1.id}),{"emails": emails})
        invitations = MembershipInvitation.objects.filter(
            invitation_sent=True, content_type_id=self.content_type_obj.id,\
             object_id=self.group1.id)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(invitations.count(), len(emails.split(",")))

    def test_accept_invitation(self):
        invitation_obj = MembershipInvitation.objects.create(
            email= "user2@example.com",
            user= self.user2, invited_by= self.user1,
            content_type_id= self.content_type_obj.id,
            object_id= self.group1.id)
        uu_id = invitation_obj.code.hex
        self.client.login(username= self.user2.username, password="a")
        res = self.client.post(reverse("django-members-roles:accept-decline-invitation",\
         kwargs= {"uu_id": uu_id}), {"accept_status": "True"})
        invitation = MembershipInvitation.objects.latest('id')
        self.assertEqual(invitation_obj.email, invitation.email)
        self.assertEqual(invitation.accepted_invitation, True)
        self.assertEqual(invitation.decline_invitation, None)

    def test_wrong_code_for_accept_invitation(self):
        invitation_obj = MembershipInvitation.objects.create(
            email= "user2@example.com",
            user= self.user2, invited_by= self.user1,
            content_type_id= self.content_type_obj.id,
            object_id= self.group1.id)
        code = uuid.uuid1()
        self.client.login(username= self.user2.username, password="a")
        res = self.client.get(reverse("django-members-roles:accept-decline-invitation",\
         kwargs= {"uu_id": code.hex }), {"accept_status": "True"})

        self.assertEqual(res.status_code, 302)

    def test_correct_code_for_accept_invitation(self):
        invitation_obj = MembershipInvitation.objects.create(
            email= "user2@example.com",
            user= self.user2, invited_by= self.user1,
            content_type_id= self.content_type_obj.id,
            object_id= self.group1.id)
        code = invitation_obj.code.hex
        self.client.login(username= self.user2.username, password="a")
        res = self.client.get(reverse("django-members-roles:accept-decline-invitation",\
         kwargs= {"uu_id": code }), {"accept_status": "True"})
        self.assertEqual(res.status_code, 200)

    def test_decline_invitation(self):
        invitation_obj = MembershipInvitation.objects.create(
            email= "user1@example.com",
            user= self.user1, invited_by= self.user2,
            content_type_id= self.content_type_obj.id,
            object_id= self.group1.id)
        uu_id = invitation_obj.code.hex
        self.client.login(username= self.user1.username, password= "a")
        self.client.post(reverse("django-members-roles:accept-decline-invitation",\
         kwargs={"uu_id": uu_id}), {"accept_status": "False"})

        invitation = MembershipInvitation.objects.latest('id')
        self.assertEqual(invitation_obj.email, invitation.email)
        self.assertEqual(invitation.accepted_invitation, None)
        self.assertEqual(invitation.decline_invitation, True)

    def test_permission_denied_for_invitation_invalid_user(self):
        invitation_obj = MembershipInvitation.objects.create(
            email= "user1@example.com",
            user= self.user1, invited_by= self.user2,
            content_type_id= self.content_type_obj.id,
            object_id= self.group2.id)
        uu_id = invitation_obj.code.hex
        self.client.login(username= self.user2.username,password="a")
        self.client.post(reverse("django-members-roles:accept-decline-invitation",\
         kwargs={"uu_id": uu_id}), {"accept_status": "True"})
        invitation = MembershipInvitation.objects.latest('id')
        self.assertEqual(invitation_obj.email, invitation.email)
        self.assertEqual(invitation.accepted_invitation, None)
        self.assertEqual(invitation.decline_invitation, None)

    def test_staff_list(self):
        self.client.logout()
        invitation_obj = MembershipInvitation.objects.create(
            email= "user3@example.com",
            invited_by= self.user1,
            content_type_id= self.content_type_obj.id,
            object_id= self.group1.id)
        uu_id = invitation_obj.code.hex
        user3 = User.objects.create_user(username="user3",
            email="user3@example.com", password="a")
        user3.is_superuser = True
        user3.save()
        """ creating generic member for user """
        generic_obj = GenericMember.objects.create(
            content_type_id=self.content_type_obj.id, object_id=self.group1.id,
            user = user3)
        self.client.login(username= user3.username, password="a")
        res = self.client.post(reverse("django-members-roles:accept-decline-invitation",\
         kwargs= {"uu_id": uu_id}), {"accept_status": "True"})
        invitation = MembershipInvitation.objects.latest('id')
        self.assertEqual(invitation_obj.id, invitation.id)
        self.assertEqual(invitation_obj.email, invitation.email)
        self.assertEqual(invitation.accepted_invitation, True)
        res = self.client.get(reverse("django-members-roles:member-list", \
            kwargs= {"content_type_id": self.content_type_obj.id,
            "object_id": self.group1.id}))
        generic_obj = GenericMember.objects.create(
            content_type_id=self.content_type_obj.id, object_id=self.group1.id,
            user = self.user2)
        members_accepted_list = list(MembershipInvitation.objects.filter(
                content_type_id=self.content_type_obj.id, object_id=self.group1.id,
                accepted_invitation=True
            ).values_list("user_id", flat=True))
        members= GenericMember.objects.filter(
            content_type_id=self.content_type_obj.id, object_id=self.group1.id,
            user_id__in=members_accepted_list)
        self.assertEqual(members.count(),res.context['staff'].count())
        self.assertEqual(list(members.values_list("user_id", flat=True)),\
         list(res.context['staff'].values_list("user_id", flat=True)))


class RolesTestCases(Common):

    def test_adding_role(self):
        self.client.login(username= self.user1.username, password= "a")
        data = {
            "name" : "role1",
            "description": "first role",
            "permissions": list(
                self.role_permission_obj.permissions.all().values_list(
                    "id", flat=True))
        }
        res = self.client.post(reverse('django-members-roles:create-and-update-role',\
         kwargs= {'content_type_id':self.content_type_obj.id,
         'object_id': self.group1.id}), data)
        role_obj = Role.objects.latest('id')
        self.assertEqual(role_obj.name, data['name'])

    def test_edit_role(self):
        self.client.login(username= self.user1.username, password= "a")
        data = {
            "name" : "role2",
            "description": "first role",
            "permissions": list(
                self.role_permission_obj.permissions.all().values_list(
                    "id", flat=True))
        }
        res = self.client.post(reverse('django-members-roles:create-and-update-role',\
         kwargs= {'content_type_id':self.content_type_obj.id,
         'object_id': self.group1.id}), data)
        role_obj = Role.objects.latest('id')
        data2 = data
        data2['name'] = "role"
        res = self.client.post("%s?role_id=%s" %(reverse(
            'django-members-roles:create-and-update-role',\
         kwargs= {'content_type_id': self.content_type_obj.id,
         'object_id': self.group1.id}), role_obj.id), data2)
        role_obj = Role.objects.get(id= role_obj.id)
        self.assertEqual(role_obj.name, data2['name'])

    def test_delete_role(self):
        self.client.login(username= self.user1.username, password= "a")
        data = {
            "name" : "role1",
            "description": "first role",
            "permissions": list(
                self.role_permission_obj.permissions.all().values_list(
                    "id", flat=True))
        }
        res = self.client.post(reverse(
            'django-members-roles:create-and-update-role',\
         kwargs= {'content_type_id':self.content_type_obj.id,
         'object_id': self.group1.id}), data)
        role_obj = Role.objects.latest('id')
        res = self.client.post(reverse('django-members-roles:delete-role',\
         kwargs= {'content_type_id': self.content_type_obj.id,
         'object_id': self.group1.id, 'pk': role_obj.id}), data)
        self.assertEqual(res.status_code, 302)
        self.assertEqual(Role.objects.filter(id=role_obj.id).count(), 0)

    def test_role_list(self):
        self.client.login(username= self.user1.username, password= "a")
        data = {
            "name" : "role1",
            "description": "first role",
            "permissions": list(
                self.role_permission_obj.permissions.all().values_list(
                    "id", flat=True))
        }
        res = self.client.post(reverse(
            'django-members-roles:create-and-update-role',\
         kwargs= {'content_type_id':self.content_type_obj.id,
         'object_id': self.group1.id}), data)
        roles = Role.objects.all()
        res = self.client.get(reverse("django-members-roles:role-list",
            kwargs={'content_type_id': self.content_type_obj.id,
         'object_id': self.group1.id}))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['roles'].count(), roles.count())


class GenericMemberRoleTestCase(Common):

    def test_add_permission_role_to_url(self):
        self.client.login(username=self.user1.username, password="a")
        project_urls_old_obj_count = ProjectUrl.objects.all().count()
        res = self.client.post(reverse("django-members-roles:update-project-urls"))
        project_urls_obj = ProjectUrl.objects.all()
        self.assertNotEqual(project_urls_old_obj_count, project_urls_obj.count())
        add_staff_url = project_urls_obj.get(name="add-member")
        self.assertEqual(add_staff_url.name, "add-member")
        genericmember_content = ContentType.objects.get(
            app_label='django_members_roles', model='genericmember')
        permission = Permission.objects.get(
            content_type= genericmember_content, codename="add_genericmember")
        url_permission_obj = UrlPermissionRequired.objects.create(
            url = add_staff_url
            )
        url_permission_obj.permissions.add(permission)
        url_permission_obj.save()

        role = Role.objects.create(name="add_staff",
            content_type=self.content_type_obj, object_id= self.group1.id
            )
        role.permissions.add(permission.id)
        role.save()
        generic_member = GenericMember.objects.create(
            user= self.user1, content_type= self.content_type_obj,
            object_id = self.group1.id
            )

        url = "%s?%s=%s&%s=%s" % (
            reverse("django-members-roles:add-member",
            kwargs={"content_type_id":self.content_type_obj.id,\
            "object_id":self.group1.id}),
            app_settings.DJANGO_MEMBERS_ROLES_QUERY_PARAM_CONTENT_TYPE_ID,
            self.content_type_obj.id,
            app_settings.DJANGO_MEMBERS_ROLES_QUERY_PARAM_OBJECT_ID,
            self.group1.id)

        emails = "user6@example.com,user7@example.com"
        res = self.client.post(url, {"emails": emails})

        self.assertEqual(res.status_code, 403)

        generic_member.role = role
        generic_member.save()

        res = self.client.post(url, {"emails": emails})

        self.assertEqual(res.status_code, 200)

    def test_update_role_to_generic_member(self):
        self.client.login(username= self.user1.username, password= "a")
        role1 = Role.objects.create(name="role1",
            content_type=self.content_type_obj, object_id= self.group1.id)
        role2 = Role.objects.create(name="role1",
            content_type=self.content_type_obj, object_id= self.group1.id)

        generic_member = GenericMember.objects.create(
            user= self.user2, content_type= self.content_type_obj,
            object_id= self.group1.id
            )
        generic_member.role = role1
        generic_member.save()

        res = self.client.post(reverse("django-members-roles:update-member-role",
            kwargs={"content_type_id":self.content_type_obj.id,\
            "object_id":self.group1.id}), data={"role_id": role2.id,\
             "user_id": self.user2.id})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['message'], "success")

        res = self.client.post(reverse("django-members-roles:update-member-role",
            kwargs={"content_type_id":self.content_type_obj.id,\
            "object_id":self.group1.id}), data={"user_id": self.user2.id})

        self.assertEqual(res.json()['error'], True)
        self.assertEqual(res.json()['message'], "required role id")

        res = self.client.post(reverse("django-members-roles:update-member-role",
            kwargs={"content_type_id":self.content_type_obj.id,\
            "object_id":self.group1.id}), data={"role_id": "null",
            "user_id": self.user2.id})

        self.assertEqual(res.json()['message'], "success")

        generic_member = GenericMember.objects.get(user= self.user2,
            content_type= self.content_type_obj,
            object_id= self.group1.id)

        self.assertEqual(generic_member.role, None)