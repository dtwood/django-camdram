# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import itertools
import datetime
import hashlib

from django.db import models, migrations
from django.template.defaultfilters import slugify
from django.core.management import call_command

def initial_data(apps, schema_editor):
    call_command('loaddata','initial_data')
    

def migrate_people(apps, schema_editor):
    OldPerson = apps.get_model('old_drama', 'ActsPeopleData')
    Person = apps.get_model('drama', 'Person')
    Group = apps.get_model('auth', 'Group')
    for op in OldPerson.objects.all():
        p = Person()
        base_slug = slugify(op.name)
        if Person.objects.filter(slug=base_slug).count() > 0:
            for i in itertools.count(2):
                slug = slugify(base_slug + '-' + str(i))
                if Person.objects.filter(slug=slug).count() == 0:
                    break
        else:
            slug = base_slug
        p.slug = slug
        p.id = op.id
        p.name = op.name
        p.desc = op.description
        p.norobots = op.norobots
        g = Group(name=p.slug)
        g.save()
        p.group = g
        p.approved=True
        p.save()

def migrate_societies(apps, schema_editor):
    OldSociety = apps.get_model('old_drama', 'ActsSocieties')
    Society = apps.get_model('drama', 'Society')
    Venue = apps.get_model('drama', 'Venue')
    Group = apps.get_model('auth', 'Group')
    for os in OldSociety.objects.all():
        if os.type == '1': #this means venue, i think.
            new = Venue()
            if os.address:
                new.address = os.address
            else:
                new.address = ''
            new.lat = os.latitude
            new.lng = os.longitude
        else:
            new = Society()
            new.shortname = os.shortname
            if os.college:
                new.college = os.college
            else:
                new.college = ''
        new.id = os.id
        new.name = os.name
        new.desc = os.description
        if os.facebook_id:
            new.facebook_id = os.facebook_id
        if os.twitter_id:
            new.twitter_id = os.twitter_id
        base_slug = slugify(new.name)
        if new.__class__.objects.filter(slug=base_slug).count() > 0:
            for i in itertools.count(2):
                slug = slugify(base_slug + '-' + str(i))
                if new.__class__.objects.filter(slug=slug).count() == 0:
                    break
        else:
            slug = base_slug
        new.slug = slug
        g = Group(name=new.slug)
        g.save()
        new.group = g
        new.approved = True
        new.save()

def migrate_shows(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    OldShow = apps.get_model('old_drama', 'ActsShows')
    Show = apps.get_model('drama', 'Show')
    Society = apps.get_model('drama', 'Society')
    Audition = apps.get_model('drama', 'Audition')
    for os in OldShow.objects.all():
        new = Show()
        new.id = os.id
        if os.socid:
            socid = os.socid
            soc = Society.objects.get(id=socid)
        else:
            try:
                soc = Society.objects.filter(name=os.society)[0]
            except IndexError:
                soc = Society(name=os.society)
                base_slug = slugify(soc.name)
                if new.__class__.objects.filter(slug=base_slug).count() > 0:
                    for i in itertools.count(2):
                        slug = slugify(base_slug + '-' + str(i))
                        if new.__class__.objects.filter(slug=slug).count() == 0:
                            break
                else:
                    slug = base_slug
                soc.slug = slug
                g = Group(name=soc.slug)
                g.save()
                soc.group = g
                soc.save()
        new.name = os.title
        new.desc = os.description
        if os.facebook_id:
            new.facebook_id = os.facebook_id
        if os.twitter_id:
            new.twitter_id = os.twitter_id
        new.author = os.author
        if os.onlinebookingurl:
            new.book = os.onlinebookingurl
        if os.prices:
            new.prices = os.prices
        base_slug = slugify(new.name)
        if new.__class__.objects.filter(slug=base_slug).count() > 0:
            for i in itertools.count(2):
                slug = slugify(base_slug + '-' + str(i))
                if new.__class__.objects.filter(slug=slug).count() == 0:
                    break
        else:
            slug = base_slug
        new.slug = slug
        g = Group(name=new.slug)
        g.save()
        new.group = g
        if os.authorizeid:
            new.approved = True
        new.save()
        new.societies.add(soc)
        new_aud = Audition(show=new)
        if os.audextra:
            new_aud.desc = os.audextra
        new_aud.save()
        


def migrate_performances(apps, schema_editor):
    Show = apps.get_model('drama', 'Show')
    OldShow = apps.get_model('old_drama', 'ActsShows')
    OldPerformance = apps.get_model('old_drama', 'ActsPerformances')
    Performance = apps.get_model('drama', 'Performance')
    Venue = apps.get_model('drama', 'Venue')
    Group = apps.get_model('auth', 'Group')
    for old in OldPerformance.objects.all():
        new = Performance()
        new.show = Show.objects.get(id=old.sid)
        new.start_date = old.startdate
        new.time = old.time
        oldshow = OldShow.objects.get(id=old.sid)
        if old.venid:
            ven = Venue.objects.get(id=old.venid)
        elif oldshow.venid:
            ven = Venue.objects.get(id=oldshow.venid)
        else:
            if old.venue:
                venue_name = old.venue
            else:
                venue_name = oldshow.venue
            try:
                ven = Venue.objects.filter(name=venue_name)[0]
            except IndexError:
                ven = Venue(name=venue_name)
                base_slug = slugify(ven.name)
                if ven.__class__.objects.filter(slug=base_slug).count() > 0:
                    for i in itertools.count(2):
                        slug = slugify(base_slug + '-' + str(i))
                        if ven.__class__.objects.filter(slug=slug).count() == 0:
                            break
                else:
                    slug = base_slug
                ven.slug = slug
                g = Group(name=ven.slug)
                g.save()
                ven.group = g
                ven.approved = False
                ven.save()
        new.venue = ven
        if old.excludedate:
            new.end_date = old.excludedate - datetime.timedelta(days=1)
            new.save()
            new2 = Performance()
            new2.show = new.show
            new2.venue = new.venue
            new2.time = new.time
            new2.start_date = old.excludedate + datetime.timedelta(days=1)
            new2.end_date = old.enddate
            new2.save()
        else:
            new.end_date = old.enddate
            new.save()

def migrate_role_instances(apps, schema_editor):
    Show = apps.get_model('drama', 'Show')
    Person = apps.get_model('drama', 'Person')
    Role = apps.get_model('drama', 'Role')
    RoleInstance = apps.get_model('drama', 'RoleInstance')
    OldRoleInstance = apps.get_model('old_drama', 'ActsShowsPeopleLink')
    cast = Role.objects.filter(cat='cast')[0]
    band = Role.objects.filter(cat='band')[0]
    prod = Role.objects.filter(cat='prod')[0]
    for old in OldRoleInstance.objects.all():
        new = RoleInstance()
        new.show = Show.objects.get(id=old.sid)
        new.person = Person.objects.get(id=old.pid)
        new.sort = old.order
        new.name = old.role
        if old.type == "cast":
            new.role = cast
        elif old.type == "band":
            new.role = band
        else:
            new.role = prod
        new.save()
            

def migrate_techieads(apps, schema_editor):
    Show = apps.get_model('drama', 'Show')
    Role = apps.get_model('drama', 'Role')
    TechieAd = apps.get_model('drama', 'TechieAd')
    TechieAdRole = apps.get_model('drama', 'TechieAdRole')
    OldTechieAd = apps.get_model('old_drama', 'ActsTechies')
    prod = Role.objects.filter(cat='prod')[0]
    for old in OldTechieAd.objects.all():
        new = TechieAd()
        new.show = Show.objects.get(id=old.showid)
        new.desc = old.techextra
        new.contact = old.contact
        deadline = old.expiry
        if old.deadlinetime:
            deadline = datetime.datetime.combine(deadline, old.deadlinetime)
        new.deadline = deadline
        new.save()
        for pos in old.positions.splitlines():
            new_pos = TechieAdRole()
            new_pos.name = pos
            new_pos.ad = new
            new_pos.role = prod
            new_pos.slug = slugify(new_pos.name)
            new_pos.save()

def migrate_users(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    OldUser = apps.get_model('old_drama', 'ActsUsers')
    for old in OldUser.objects.all():
        new = User()
        new.id = old.id
        new.first_name = old.name
        new.email = old.email
        new.date_joined = old.registered
        new.is_active = True
        new.password = '{alg}${salt}${hash}'.format(alg='md5', hash=old.pass_field, salt='')
        new.username = hashlib.md5(new.email.encode('utf-8')).hexdigest()[0:30]
        new.save()

def migrate_access(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Access = apps.get_model('old_drama', 'ActsAccess')
    Show = apps.get_model('drama', 'Show')
    Society = apps.get_model('drama', 'Society')
    Venue = apps.get_model('drama', 'Venue')
    for item in Access.objects.all():
        user = User.objects.get(id=item.uid)
        if item.type == 'security':
            user.is_superuser = True
            user.is_staff = True
            user.save()
        elif item.type == 'show':
            obj = Show.objects.get(id=item.rid)
            obj.group.user_set.add(user)
            obj.save()
        elif item.type == 'society':
            try:
                obj = Society.objects.get(id=item.rid)
            except Society.DoesNotExist:
                obj = Venue.objects.get(id=item.rid)
            obj.group.user_set.add(user)
            obj.save()
        else:
            print('Unrecognised ActsAccess type: ' + item.type)
    
def migrate_pending_access(apps, schema_editor):
    Show = apps.get_model('drama', 'Show')
    Society = apps.get_model('drama', 'Society')
    Venue = apps.get_model('drama', 'Venue')
    Access = apps.get_model('old_drama', 'ActsPendingAccess')
    PendingGroupMember = apps.get_model('drama', 'PendingGroupMember')
    for item in Access.objects.all():
        if item.type == 'show':
            group = Show.objects.get(id=item.rid).group
            pg = PendingGroupMember(email = item.email, group = group)
            pg.save()
        elif item.type == 'society':
            try:
                group = Society.objects.get(id=item.rid).group
            except Society.DoesNotExist:
                group = Venue.objects.get(id=item.rid).group
            pg = PendingGroupMember(email = item.email, group = group)
            pg.save()
        else:
            print('Unrecognised ActsPendingAccess type: ' + item.type)
    
        
def migrate_applications(apps, schema_editor):
    Show = apps.get_model('drama', 'Show')
    Society = apps.get_model('drama', 'Society')
    Venue = apps.get_model('drama', 'Venue')
    Application = apps.get_model('drama', 'Application')
    ShowApplication = apps.get_model('drama', 'ShowApplication')
    SocietyApplication = apps.get_model('drama', 'SocietyApplication')
    VenueApplication = apps.get_model('drama', 'VenueApplication')
    OldApplication = apps.get_model('old_drama', 'ActsApplications')
    for old in OldApplication.objects.all():
        if old.showid:
            new = ShowApplication()
            parent = Show.objects.get(id=old.showid)
            new.show = parent
        else:
            try:
                parent = Society.objects.get(id=old.socid)
                new = SocietyApplication()
                new.society = parent
            except Society.DoesNotExist:
                new = VenueApplication()
                parent = Venue.objects.get(id=old.socid)
                new.venue = parent
        new.name = old.text
        new.desc = old.furtherinfo
        new.deadline = datetime.datetime.combine(old.deadlinedate, old.deadlinetime)
        base_slug = slugify(parent.name + '-' + new.name)
        if Application.objects.filter(slug=base_slug).count() > 0:
            for i in itertools.count(2):
                slug = slugify(base_slug + '-' + str(i))
                if Application.objects.filter(slug=slug).count() == 0:
                    break
        else:
            slug = base_slug
        new.slug = slug
        new.save()
    
    
def migrate_auditions(apps, schema_editor):
    Show = apps.get_model('drama', 'Show')
    OldAudition = apps.get_model('old_drama', 'ActsAuditions')
    AuditionInstance = apps.get_model('drama', 'AuditionInstance')
    for old in OldAudition.objects.all():
        show = Show.objects.get(id=old.showid)
        audition = show.audition
        if old.nonscheduled:
            audition.contact = old.location
            audition.save()
        else:
            new = AuditionInstance(audition=audition)
            new.location = old.location
            new.start_time = old.starttime
            new.end_datetime = datetime.datetime.combine(old.date, old.endtime)
            new.save()
    
    

class Migration(migrations.Migration):

    dependencies = [
        ('old_drama', '0001_initial'),
        ('drama', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(initial_data),
        migrations.RunPython(migrate_people),
        migrations.RunPython(migrate_societies),
        migrations.RunPython(migrate_shows),
        migrations.RunPython(migrate_performances),
        migrations.RunPython(migrate_role_instances),
        migrations.RunPython(migrate_techieads),
        migrations.RunPython(migrate_users),
        migrations.RunPython(migrate_access),
        migrations.RunPython(migrate_pending_access),
        migrations.RunPython(migrate_applications),
        migrations.RunPython(migrate_auditions),

    ]
