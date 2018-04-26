from __future__ import absolute_import, unicode_literals
from celery import shared_task

from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib.sites.models import Site

from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)


@shared_task
def sum_of_two_numbers(num1, num2):
    return num1 + num2
