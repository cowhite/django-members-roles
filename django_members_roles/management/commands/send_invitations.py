from django.core.management.base import BaseCommand, CommandError

from interviews.models import PublicTestCount, Interview
from django.utils import timezone
from django_members_roles.models import BulkInvitation

import datetime

class Command(BaseCommand):
    def handle(self, *args, **options):
        invitations = BulkInvitation.objects.filter(invitation_sent=False)
        for invitation in invitations:
            invitation.send_invitations()
