# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import drama.models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0003_auto_20141005_1357'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('desc', models.TextField(verbose_name='Description', blank=True)),
                ('contact', models.CharField(blank=True, max_length=200)),
                ('deadline', models.DateTimeField()),
                ('slug', models.SlugField(blank=True, unique=True, editable=False, max_length=200)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ApprovalQueueItem',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('created_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Audition',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('desc', models.TextField(verbose_name='Description', blank=True)),
                ('contact', models.CharField(blank=True, max_length=200)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AuditionInstance',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('end_datetime', models.DateTimeField()),
                ('start_time', models.TimeField()),
                ('location', models.CharField(max_length=200)),
                ('audition', models.ForeignKey(to='drama.Audition')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EmailList',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('desc', models.TextField(verbose_name='Description', blank=True)),
                ('slug', models.SlugField(unique=True, max_length=200)),
                ('approved', models.BooleanField(default=False, editable=False)),
                ('html_template', models.TextField()),
                ('plaintext_template', models.TextField()),
                ('default_address', models.EmailField(max_length=75)),
                ('default_header', models.TextField()),
                ('default_subject', models.CharField(max_length=256)),
                ('from_addr', models.EmailField(verbose_name='From Address', max_length=75)),
                ('date_format', models.CharField(default='D jS F Y', max_length=50)),
                ('group', models.OneToOneField(to='auth.Group')),
            ],
            options={
                'permissions': (('view_emaillists', 'View Email Lists'), ('approve_emaillist', 'Approve Email Lists')),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LogItem',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('cat', models.CharField(verbose_name='Type', choices=[('CREATE', 'Create'), ('EDIT', 'Edit'), ('APPROVE', 'Approval Change'), ('ADMIN', 'Admin Change'), ('DELETE', 'Delete')], max_length=10)),
                ('datetime', models.DateTimeField()),
                ('object_id', models.PositiveIntegerField()),
                ('desc', models.TextField()),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PendingAdmin',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('email', models.EmailField(max_length=75)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PendingGroupMember',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('email', models.EmailField(max_length=75)),
                ('group', models.ForeignKey(to='auth.Group')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Performance',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('time', models.TimeField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('desc', models.TextField(verbose_name='Description', blank=True)),
                ('slug', models.SlugField(unique=True, max_length=200)),
                ('approved', models.BooleanField(default=False, editable=False)),
                ('norobots', models.BooleanField()),
                ('group', models.OneToOneField(to='auth.Group')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL, blank=True, null=True)),
            ],
            options={
                'permissions': (('approve_person', 'Approve Person'),),
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('desc', models.TextField(verbose_name='Description', blank=True)),
                ('slug', models.SlugField(unique=True, max_length=200)),
                ('approved', models.BooleanField(default=False, editable=False)),
                ('cat', models.CharField(verbose_name='Role Category', choices=[('cast', 'Cast'), ('band', 'Band'), ('prod', 'Production Team')], max_length=4)),
                ('group', models.OneToOneField(to='auth.Group')),
            ],
            options={
                'permissions': (('approve_role', 'Approve Role'),),
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RoleInstance',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('name', models.CharField(verbose_name='Role name', max_length=200)),
                ('sort', models.IntegerField(default=1000)),
                ('person', models.ForeignKey(to='drama.Person')),
                ('role', models.ForeignKey(verbose_name='Role Type', to='drama.Role')),
            ],
            options={
                'ordering': ['sort'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Show',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('desc', models.TextField(verbose_name='Description', blank=True)),
                ('slug', models.SlugField(unique=True, max_length=200)),
                ('approved', models.BooleanField(default=False, editable=False)),
                ('book', models.URLField(verbose_name='Booking Link', blank=True)),
                ('prices', models.CharField(blank=True, max_length=30)),
                ('author', models.CharField(blank=True, max_length=200)),
                ('image', models.ImageField(blank=True, upload_to='images/')),
                ('group', models.OneToOneField(to='auth.Group')),
            ],
            options={
                'permissions': (('approve_show', 'Approve Show'),),
                'ordering': ['name'],
            },
            bases=(models.Model, drama.models.DramaSocialMixin),
        ),
        migrations.CreateModel(
            name='ShowApplication',
            fields=[
                ('application_ptr', models.OneToOneField(parent_link=True, to='drama.Application', auto_created=True, primary_key=True, serialize=False)),
                ('show', models.ForeignKey(to='drama.Show')),
            ],
            options={
            },
            bases=('drama.application',),
        ),
        migrations.CreateModel(
            name='Society',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('desc', models.TextField(verbose_name='Description', blank=True)),
                ('slug', models.SlugField(unique=True, max_length=200)),
                ('approved', models.BooleanField(default=False, editable=False)),
                ('shortname', models.CharField(verbose_name='Abbreviaiton', max_length=100)),
                ('college', models.CharField(blank=True, max_length=100)),
                ('image', models.ImageField(verbose_name='Logo', blank=True, upload_to='images/')),
                ('group', models.OneToOneField(to='auth.Group')),
            ],
            options={
                'permissions': (('approve_society', 'Approve Society'),),
                'ordering': ['name'],
            },
            bases=(models.Model, drama.models.DramaSocialMixin),
        ),
        migrations.CreateModel(
            name='SocietyApplication',
            fields=[
                ('application_ptr', models.OneToOneField(parent_link=True, to='drama.Application', auto_created=True, primary_key=True, serialize=False)),
                ('society', models.ForeignKey(to='drama.Society')),
            ],
            options={
            },
            bases=('drama.application',),
        ),
        migrations.CreateModel(
            name='TechieAd',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('desc', models.TextField(verbose_name='Description', blank=True)),
                ('contact', models.CharField(max_length=200)),
                ('deadline', models.DateTimeField()),
                ('show', models.OneToOneField(to='drama.Show')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TechieAdRole',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('desc', models.TextField(verbose_name='Description', blank=True)),
                ('slug', models.SlugField(blank=True, editable=False, max_length=200)),
                ('ad', models.ForeignKey(to='drama.TechieAd')),
                ('role', models.ForeignKey(verbose_name='Role Type', to='drama.Role')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TermDate',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('year', models.IntegerField(choices=[(2000, 2000), (2001, 2001), (2002, 2002), (2003, 2003), (2004, 2004), (2005, 2005), (2006, 2006), (2007, 2007), (2008, 2008), (2009, 2009), (2010, 2010), (2011, 2011), (2012, 2012), (2013, 2013), (2014, 2014), (2015, 2015)])),
                ('term', models.CharField(choices=[('Terms', (('MT', 'Michaelmas Term'), ('LT', 'Lent Term'), ('ET', 'Easter Term'))), ('Breaks', (('CB', 'Christmas Break'), ('EB', 'Easter Break'), ('SB', 'Summer Break')))], max_length=2)),
                ('start', models.DateField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Venue',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('desc', models.TextField(verbose_name='Description', blank=True)),
                ('slug', models.SlugField(unique=True, max_length=200)),
                ('approved', models.BooleanField(default=False, editable=False)),
                ('address', models.CharField(blank=True, max_length=200)),
                ('lat', models.FloatField(verbose_name='Latitude', blank=True, null=True)),
                ('lng', models.FloatField(verbose_name='Longditude', blank=True, null=True)),
                ('group', models.OneToOneField(to='auth.Group')),
            ],
            options={
                'permissions': (('approve_venue', 'Approve Venue'),),
                'ordering': ['name'],
            },
            bases=(models.Model, drama.models.DramaSocialMixin),
        ),
        migrations.CreateModel(
            name='VenueApplication',
            fields=[
                ('application_ptr', models.OneToOneField(parent_link=True, to='drama.Application', auto_created=True, primary_key=True, serialize=False)),
                ('venue', models.ForeignKey(to='drama.Venue')),
            ],
            options={
            },
            bases=('drama.application',),
        ),
        migrations.AddField(
            model_name='show',
            name='societies',
            field=models.ManyToManyField(to='drama.Society'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='roleinstance',
            name='show',
            field=models.ForeignKey(to='drama.Show'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='performance',
            name='show',
            field=models.ForeignKey(to='drama.Show'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='performance',
            name='venue',
            field=models.ForeignKey(to='drama.Venue'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='pendingadmin',
            name='show',
            field=models.ForeignKey(to='drama.Show'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='audition',
            name='show',
            field=models.OneToOneField(to='drama.Show'),
            preserve_default=True,
        ),
    ]
