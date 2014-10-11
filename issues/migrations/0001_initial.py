# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=200)),
                ('desc', models.TextField(blank=True)),
                ('active', models.BooleanField(default=True)),
                ('email', models.EmailField(max_length=75)),
                ('opened', models.DateTimeField()),
                ('assigned_user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, blank=True)),
            ],
            options={
                'ordering': ['-opened'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sender', models.CharField(max_length=260)),
                ('body', models.TextField()),
                ('recieved', models.DateTimeField()),
                ('issue', models.ForeignKey(to='issues.Issue')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
