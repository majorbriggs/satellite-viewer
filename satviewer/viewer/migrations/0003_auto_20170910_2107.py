# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-09-10 21:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('viewer', '0002_satelliteimage_source'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='satelliteimage',
            name='id',
        ),
        migrations.AlterField(
            model_name='satelliteimage',
            name='aws_bucket_uri',
            field=models.TextField(primary_key=True, serialize=False),
        ),
    ]
