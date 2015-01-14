# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('drama', '0002_auto_20150113_0043'),
    ]

    operations = [
        migrations.AlterField(
            model_name='show',
            name='facebook_since',
            field=models.CharField(max_length=100, blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='show',
            name='twitter_since',
            field=models.CharField(max_length=100, blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='socialpost',
            name='link',
            field=models.URLField(max_length=500, blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='socialpost',
            name='picture',
            field=models.URLField(max_length=500, blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='society',
            name='facebook_since',
            field=models.CharField(max_length=100, blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='society',
            name='twitter_since',
            field=models.CharField(max_length=100, blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='venue',
            name='facebook_since',
            field=models.CharField(max_length=100, blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='venue',
            name='twitter_since',
            field=models.CharField(max_length=100, blank=True, null=True),
        ),
    ]
