# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-04-28 06:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_roles', '0006_role_permissions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='role',
            name='permissions',
            field=models.ManyToManyField(to='auth.Permission'),
        ),
    ]
