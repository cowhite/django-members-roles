from __future__ import absolute_import, unicode_literals
from celery import shared_task

from django.contrib.auth.models import User
from django.conf import settings

from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_invitations_task(bulkinvitation_id):

    from .models import BulkInvitation

    invitation = BulkInvitation.objects.get(id=bulkinvitation_id)
    invitation.send_invitations()
