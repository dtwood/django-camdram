# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-08 02:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drama', '0004_auto_20160508_0326'),
    ]

    operations = [
        migrations.AlterField(
            model_name='society',
            name='shortname',
            field=models.CharField(max_length=100, verbose_name='Abbreviation'),
        ),
    ]
