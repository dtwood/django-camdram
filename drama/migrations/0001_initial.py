# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import drama.models
from django.conf import settings


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
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('desc', models.TextField(blank=True, verbose_name='Description')),
                ('contact', models.CharField(max_length=200, blank=True)),
                ('deadline', models.DateTimeField()),
                ('slug', models.SlugField(max_length=200, blank=True, unique=True, editable=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ApprovalQueueItem',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
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
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('desc', models.TextField(blank=True, verbose_name='Description')),
                ('contact', models.CharField(max_length=200, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AuditionInstance',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
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
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('desc', models.TextField(blank=True, verbose_name='Description')),
                ('slug', models.SlugField(max_length=200, unique=True)),
                ('approved', models.BooleanField(editable=False, default=False)),
                ('html_template', models.TextField()),
                ('plaintext_template', models.TextField()),
                ('default_address', models.EmailField(max_length=75)),
                ('default_header', models.TextField()),
                ('default_subject', models.CharField(max_length=256)),
                ('from_addr', models.EmailField(max_length=75, verbose_name='From Address')),
                ('date_format', models.CharField(max_length=50, default='D jS F Y')),
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
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('cat', models.CharField(max_length=10, choices=[('CREATE', 'Create'), ('EDIT', 'Edit'), ('APPROVE', 'Approval Change'), ('ADMIN', 'Admin Change'), ('DELETE', 'Delete')], verbose_name='Type')),
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
            name='PendingGroupMember',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
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
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
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
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('desc', models.TextField(blank=True, verbose_name='Description')),
                ('slug', models.SlugField(max_length=200, unique=True)),
                ('approved', models.BooleanField(editable=False, default=False)),
                ('norobots', models.BooleanField()),
                ('group', models.OneToOneField(to='auth.Group')),
                ('user', models.OneToOneField(blank=True, null=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['name'],
                'permissions': (('approve_person', 'Approve Person'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('desc', models.TextField(blank=True, verbose_name='Description')),
                ('slug', models.SlugField(max_length=200, unique=True)),
                ('approved', models.BooleanField(editable=False, default=False)),
                ('cat', models.CharField(max_length=4, choices=[('cast', 'Cast'), ('band', 'Band'), ('prod', 'Production Team')], verbose_name='Role Category')),
                ('group', models.OneToOneField(to='auth.Group')),
            ],
            options={
                'ordering': ['name'],
                'permissions': (('approve_role', 'Approve Role'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RoleInstance',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Role name')),
                ('sort', models.IntegerField(default=1000)),
                ('person', models.ForeignKey(to='drama.Person')),
                ('role', models.ForeignKey(to='drama.Role', verbose_name='Role Type')),
            ],
            options={
                'ordering': ['sort'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Show',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('desc', models.TextField(blank=True, verbose_name='Description')),
                ('slug', models.SlugField(max_length=200, unique=True)),
                ('approved', models.BooleanField(editable=False, default=False)),
                ('book', models.URLField(blank=True, verbose_name='Booking Link')),
                ('prices', models.CharField(max_length=30, blank=True)),
                ('author', models.CharField(max_length=200, blank=True)),
                ('image', models.ImageField(blank=True, upload_to='images/')),
                ('group', models.OneToOneField(to='auth.Group')),
            ],
            options={
                'ordering': ['name'],
                'permissions': (('approve_show', 'Approve Show'),),
            },
            bases=(models.Model, drama.models.DramaSocialMixin),
        ),
        migrations.CreateModel(
            name='ShowApplication',
            fields=[
                ('application_ptr', models.OneToOneField(to='drama.Application', primary_key=True, serialize=False, parent_link=True, auto_created=True)),
                ('show', models.ForeignKey(to='drama.Show')),
            ],
            options={
            },
            bases=('drama.application',),
        ),
        migrations.CreateModel(
            name='Society',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('desc', models.TextField(blank=True, verbose_name='Description')),
                ('slug', models.SlugField(max_length=200, unique=True)),
                ('approved', models.BooleanField(editable=False, default=False)),
                ('shortname', models.CharField(max_length=100, verbose_name='Abbreviaiton')),
                ('college', models.CharField(max_length=100, blank=True)),
                ('image', models.ImageField(blank=True, verbose_name='Logo', upload_to='images/')),
                ('group', models.OneToOneField(to='auth.Group')),
            ],
            options={
                'ordering': ['name'],
                'permissions': (('approve_society', 'Approve Society'),),
            },
            bases=(models.Model, drama.models.DramaSocialMixin),
        ),
        migrations.CreateModel(
            name='SocietyApplication',
            fields=[
                ('application_ptr', models.OneToOneField(to='drama.Application', primary_key=True, serialize=False, parent_link=True, auto_created=True)),
                ('society', models.ForeignKey(to='drama.Society')),
            ],
            options={
            },
            bases=('drama.application',),
        ),
        migrations.CreateModel(
            name='TechieAd',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('desc', models.TextField(blank=True, verbose_name='Description')),
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
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('desc', models.TextField(blank=True, verbose_name='Description')),
                ('slug', models.SlugField(max_length=200, blank=True, editable=False)),
                ('ad', models.ForeignKey(to='drama.TechieAd')),
                ('role', models.ForeignKey(to='drama.Role', verbose_name='Role Type')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TermDate',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('year', models.IntegerField(choices=[(2000, 2000), (2001, 2001), (2002, 2002), (2003, 2003), (2004, 2004), (2005, 2005), (2006, 2006), (2007, 2007), (2008, 2008), (2009, 2009), (2010, 2010), (2011, 2011), (2012, 2012), (2013, 2013), (2014, 2014), (2015, 2015)])),
                ('term', models.CharField(max_length=2, choices=[('Terms', (('MT', 'Michaelmas Term'), ('LT', 'Lent Term'), ('ET', 'Easter Term'))), ('Breaks', (('CB', 'Christmas Break'), ('EB', 'Easter Break'), ('SB', 'Summer Break')))])),
                ('start', models.DateField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Venue',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('desc', models.TextField(blank=True, verbose_name='Description')),
                ('slug', models.SlugField(max_length=200, unique=True)),
                ('approved', models.BooleanField(editable=False, default=False)),
                ('address', models.CharField(max_length=200, blank=True)),
                ('lat', models.FloatField(blank=True, null=True, verbose_name='Latitude')),
                ('lng', models.FloatField(blank=True, null=True, verbose_name='Longditude')),
                ('group', models.OneToOneField(to='auth.Group')),
            ],
            options={
                'ordering': ['name'],
                'permissions': (('approve_venue', 'Approve Venue'),),
            },
            bases=(models.Model, drama.models.DramaSocialMixin),
        ),
        migrations.CreateModel(
            name='VenueApplication',
            fields=[
                ('application_ptr', models.OneToOneField(to='drama.Application', primary_key=True, serialize=False, parent_link=True, auto_created=True)),
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
            model_name='audition',
            name='show',
            field=models.OneToOneField(to='drama.Show'),
            preserve_default=True,
        ),
    ]
