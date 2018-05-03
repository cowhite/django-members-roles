from django.test import TestCase

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse

from django_roles.models import (GenericMember, BulkInvitation,\
 Role, RolePermission, MembershipInvitation)
from . import app_settings

import time

class GenericMemberTestCase(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(username= "user1", password= "a", email= "user1@example.com")
        self.user1.is_superuser= True
        self.user1.save()

        self.user2 = User.objects.create_user(username= "user2", password= "a", email= "user2@example.com")
        self.user2.is_superuser= True
        self.user2.save()

        self.content_obj = ContentType.objects.get(model= app_settings.DJANGO_ROLES_TEST_CASE_MODEL_NAME,
            app_label= app_settings.DJANGO_ROLES_TEST_CAES_APP_LABEL)

    # def test_sending_invitation(self):
    #     print(self.user.is_superuser)
    #     self.client.login(username="a",password="a")
    #     content_obj = ContentType.objects.get(model=app_settings.TEST_CASE_MODEL_NAME,
    #         app_label=app_settings.TEST_CAES_APP_LABEL)
    #     res = self.client.post(reverse("add-staff", kwargs={"content_type_id":content_obj.id,\
    #         "object_id":self.user.id}),{"emails":"user1@example.com,user2@example.com"})
    #     self.assertEqual(res.status_code, 200)
        #self.assertTrue(res.context['user'].is_active)

    def test_accept_invitation(self):
        invitation_obj = MembershipInvitation.objects.create(email= "user2@example.com",
            user= self.user2, invited_by= self.user1, content_type_id= self.content_obj.id,
            object_id= self.user1.id)
        uu_id = invitation_obj.code.hex
        self.client.login(username= self.user2, password="a")
        self.client.post(reverse("accept-decline-invitation",\
         kwargs= {"uu_id": uu_id}), {"accept_status": "True"})
        invitation = MembershipInvitation.objects.latest('id')
        self.assertEqual(invitation_obj.email, invitation.email)
        self.assertEqual(invitation.accepted_invitation, True)
        self.assertEqual(invitation.decline_invitation, None)


    def test_decline_invitation(self):
        invitation_obj = MembershipInvitation.objects.create(email= "user1@example.com",
            user= self.user1, invited_by= self.user2, content_type_id= self.content_obj.id,
            object_id=self.user1.id)
        uu_id = invitation_obj.code.hex
        self.client.login(username= self.user1, password= "a")
        self.client.post(reverse("accept-decline-invitation",\
         kwargs={"uu_id": uu_id}), {"accept_status": "False"})
        invitation = MembershipInvitation.objects.latest('id')
        self.assertEqual(invitation_obj.email, invitation.email)
        self.assertEqual(invitation.accepted_invitation, None)
        self.assertEqual(invitation.decline_invitation, True)

    def test_permission_denied_for_invitation_invalid_user(self):
        invitation_obj = MembershipInvitation.objects.create(email= "user1@example.com",
            user= self.user1, invited_by= self.user2, content_type_id= self.content_obj.id,
            object_id= self.user2.id)
        uu_id = invitation_obj.code.hex
        self.client.login(username= self.user2,password="a")
        self.client.post(reverse("accept-decline-invitation",\
         kwargs={"uu_id": uu_id}), {"accept_status": "True"})
        invitation = MembershipInvitation.objects.latest('id')
        self.assertEqual(invitation_obj.email, invitation.email)
        self.assertEqual(invitation.accepted_invitation, None)
        self.assertEqual(invitation.decline_invitation, None)
