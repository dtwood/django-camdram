import math
import itertools
import drama
from django.db import models, IntegrityError
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
from datetime import date, timedelta, datetime
from django.conf import settings
from django.contrib import auth
from django.utils.safestring import mark_safe
from django.utils.html import escape
from guardian.shortcuts import assign_perm, get_objects_for_user, remove_perm, get_users_with_perms
from django.utils import timezone
from django.shortcuts import redirect
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
import reversion
import pystache
from django.template import defaultfilters

class ApprovalQueueItem(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def get_ignore_url(self):
        return reverse('approval-ignore', kwargs={'key':self.id})

    def get_approve_url(self):
        return reverse('approval-approve', kwargs={'key':self.id})


class DramaObjectQuerySet(models.query.QuerySet):
    def approved(self):
        return self.filter(approved=True)

    def unapproved(self):
        return self.filter(approved=False)
    

DramaObjectManager = models.Manager.from_queryset(DramaObjectQuerySet)


class ShowApprovedQuerySet(models.query.QuerySet):
    def approved(self):
        return self.filter(show__approved=True)

    def unapproved(self):
        return self.filter(show__approved=False)

ShowApprovedManager = models.Manager.from_queryset(ShowApprovedQuerySet)

class AdvertManager(ShowApprovedManager):
    def get_queryset(self):
        return super(AdvertManager, self).get_queryset().annotate(closing_night=models.Max('show__performance__end_date'), opening_night=models.Min('show__performance__start_date'))
    

class ShowManager(DramaObjectManager):
    def get_queryset(self):
        return super(ShowManager, self).get_queryset().annotate(end_date=models.Max('performance__end_date'), start_date=models.Min('performance__start_date'))

    
class AuditionInstanceQuerySet(models.query.QuerySet):
    def approved(self):
        return self.filter(audition__show__approved=True)
    
    def unapproved(self):
        return self.filter(audition__show__approved=False)

AuditionInstanceManager = models.Manager.from_queryset(AuditionInstanceQuerySet)


class DramaObjectModel(models.Model):
    objects = DramaObjectManager()
    queueitem = GenericRelation(ApprovalQueueItem)
    group = models.OneToOneField(auth.models.Group)
    name = models.CharField(max_length=200)
    desc = models.TextField('Description', blank=True)
    slug = models.SlugField(max_length=200, unique=True)
    approved = models.BooleanField(editable=False, default=False)
    has_applications = False

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            if self.__class__.objects.filter(slug=base_slug).count() > 0:
                for i in itertools.count(2):
                    slug = slugify(base_slug + '-' + str(i))
                    if Show.objects.filter(slug=slug).count() == 0:
                        break
            else:
                slug = base_slug
            self.slug = slug
        try:
            self.group
        except ObjectDoesNotExist:
            new_group = auth.models.Group(name=self.slug)
            new_group.save()
            self.group = new_group
        result = super(DramaObjectModel, self).save(*args, **kwargs)
        assign_perm('drama.change_' + self.class_name(), self.group, self)
        return result

    @classmethod
    def class_name(cls):
        return cls.__name__.lower()

    def get_url(self, action):
        return reverse(self.class_name() + '-' + action, kwargs={'slug': self.slug})
    
    def get_absolute_url(self):
        return self.get_url('detail')

    def get_edit_url(self):
        return self.get_url('edit')

    def get_remove_url(self):
        return self.get_url('remove')

    @classmethod
    def get_list_url(cls):
        return reverse(cls.class_name() + '-list')

    def get_approve_url(self):
        return self.get_url('approve')

    def get_unapprove_url(self):
        return self.get_url('unapprove')

    def get_applications_url(self):
        return self.get_url('applications')

    def get_admins_url(self):
        return self.get_url('admins')

    def get_admin_revoke_url(self):
        return self.get_url('revoke-admin')

    def get_pending_admin_revoke_url(self):
        return self.get_url('revoke-pending-admin')

    def get_admin_interface_url(self):
        return reverse('admin:drama_{0}_change'.format(self.class_name()), args=[self.id])

    def get_log_url(self):
        return '/admin/drama/logitem/?content_type_id__exact={0}&object_id__exact={1}'.format(ContentType.objects.get_for_model(self).id,self.id)
    
    def get_link(self, override_approval=False):
        """
        Get link text for the item, with appropriate <a> tag if the item is approved.
        """
        if self.approved or override_approval:
            return mark_safe('<a href="{0}">{1}</a>'.format(self.get_absolute_url(), escape(self.name)))
        else:
            return self.name

    def get_link_always(self):
        return self.get_link(override_approval=True)

    def approve(self):
        self.approved = True
        self.save()
        ctype = ContentType.objects.get_for_model(self)
        for item in ApprovalQueueItem.objects.filter(content_type=ctype, object_id=self.id):
            item.delete()
    approve.alters_data = True

    def unapprove(self):
        self.approved = False
        self.save()
    unapprove.alters_data = True

    def get_admins(self):
        """
        Return the current admins.
        """
        return self.group.user_set.all()

    def get_pending_admins(self):
        """
        return the pending admins
        """
        return self.group.pendinggroupmember_set.all()
    
    def add_admin(self, email):
        """
        Add the user with this email address to the organization admins.
        If the user does not exist, add the request to the pending admins list.
        """
        try:
            user = auth.get_user_model().objects.filter(email=email)[0]
            self.group.user_set.add(user)
        except IndexError:
            item = PendingGroupMember(email=email, group=self.group)
            item.save()
    add_admin.alters_data = True
    
    def remove_admin(self, username):
        """
        Remove the user with that username from the organization admins.
        """
        try:
            user = auth.get_user_model().objects.filter(username=username)[0]
            self.group.user_set.remove(user)
        except IndexError:
            pass
    remove_admin.alters_data = True

    def remove_pending_admin(self, email):
        for pg in PendingGroupMember.objects.filter(group=self.group, email=email):
            pg.delete()
    remove_pending_admin.alters_data = True

    def grant_admin(self, user):
        self.group.user_set.add(user)
    grant_admin.alters_data=True

    def revoke_admin(self, user):
        self.group.user_set.remove(user)
    revoke_admin.alters_data = True


class Person(DramaObjectModel):
    objects = DramaObjectManager()
    user = models.OneToOneField(settings.AUTH_USER_MODEL, blank=True, null=True)

    class Meta:
        ordering = ['name']
        permissions = (
            ('approve_person', 'Approve Person'),
            )

    def __str__(self):
        return self.name

    def get_shows(self):
        return Show.objects.approved().filter(roleinstance__person=self).distinct()
    
    @property
    def num_shows(self):
        return self.get_shows().count()

    @property
    def first_active(self):
        try:
            return self.get_shows().order_by('start_date')[0].start_date
        except IndexError:
            return None

    @property
    def last_active(self):
        try:
            return self.get_shows().order_by('-end_date')[0].end_date
        except IndexError:
            return None

    @property
    def dec_string(self):
        if self.last_active:
            if date.today() - self.last_active < timedelta(days=365):
                label = 'Active'
            else:
                label = 'Was Active: ' + \
                    self.first_active.strftime('%b %y') + \
                    ' - ' + self.last_active.strftime('%b %y')
            return '(' + label + ', Shows: ' + str(self.num_shows) + ')'
        else:
            return ''

    def get_roles(self):
        return RoleInstance.objects.approved().filter(person=self).annotate(end_date=models.Max('show__performance__end_date'), start_date=models.Min('show__performance__start_date'))

    def get_past_roles(self):
        return self.get_roles().exclude(end_date__gte=timezone.now()).order_by('-end_date','start_date')
    
    def get_current_roles(self):
        return self.get_roles().filter(start_date__lte=timezone.now()).filter(end_date__gte=timezone.now()).order_by('end_date','start_date')
    
    def get_future_roles(self):
        return self.get_roles().exclude(start_date__lte=timezone.now()).order_by('start_date','end_date')

    def link_user(self, user):
        try:
            user.person
        except Person.DoesNotExist:
            pass
        else:
            #May want to think about making this stricter
           remove_perm('change_person', user, user.person)
        self.user = user
        self.save()
        assign_perm('change_person', user, self)
        user.first_name = self.name
        user.save()
        return redirect(self.get_absolute_url())
    link_user.alters_data=True

    @property
    def user_email(self):
        if self.user:
            return self.user.email
    



class Venue(DramaObjectModel):
    objects = DramaObjectManager()

    def __str__(self):
        return self.name
    has_applications = True
    address = models.CharField(max_length=200, blank=True)
    lat = models.FloatField('Latitude', blank=True)
    lng = models.FloatField('Longditude', blank=True)

    class Meta:
        ordering = ['name']
        permissions = (
            ('approve_venue', 'Approve Venue'),
            )

    @property
    def dec_string(self):
        return ''

    def get_applications(self):
        return VenueApplication.objects.filter(venue=self)

    def get_shows(self):
        return Show.objects.approved().filter(performance__venue=self).distinct()

    def get_performances(self):
        return Performance.objects.approved().filter(venue=self)

    def get_auditions(self):
        return AuditionInstance.objects.approved().filter(audition__show__performance__venue=self).filter(end_datetime__gte=timezone.now()).order_by('end_datetime', 'start_time').distinct()
    
    def get_showapps(self):
        return ShowApplication.objects.approved().filter(show__performance__venue=self).filter(deadline__gte=timezone.now()).order_by('deadline').distinct()

    def get_venueapps(self):
        return VenueApplication.objects.filter(venue=self).filter(deadline__gte=timezone.now()).order_by('deadline')

    def get_techieads(self):
        return TechieAd.objects.approved().filter(show__performance__venue=self).filter(deadline__gte=timezone.now()).order_by('deadline').distinct()

    def get_safe_context(self, date_format):
        return {'name':self.name,
                'url': settings.DOMAIN_FOR_URI + self.get_absolute_url(),
                }
        

class Society(DramaObjectModel):
    objects = DramaObjectManager()
    shortname = models.CharField(max_length=100, verbose_name="Abbreviaiton")
    image = models.ImageField(
        upload_to='images/', blank=True, verbose_name="Logo")
    has_applications = True

    class Meta:
        ordering = ['name']
        permissions = (
            ('approve_society', 'Approve Society'),
            )

    def __str__(self):
        return self.name

    @property
    def dec_string(self):
        return ''

    def get_applications(self):
        return SocietyApplication.objects.filter(society=self)
    
    def get_shows(self):
        return self.show_set.approved()

    def get_performances(self):
        return Performance.objects.approved().filter(show__societies=self)

    def get_auditions(self):
        return AuditionInstance.objects.approved().filter(audition__show__societies=self).filter(end_datetime__gte=timezone.now()).order_by('end_datetime', 'start_time').distinct()
    
    def get_showapps(self):
        return ShowApplication.objects.approved().filter(show__societies=self).filter(deadline__gte=timezone.now()).order_by('deadline').distinct()

    def get_societyapps(self):
        return SocietyApplication.objects.filter(society=self).filter(deadline__gte=timezone.now()).order_by('deadline')

    def get_techieads(self):
        return TechieAd.objects.approved().filter(show__societies=self).filter(deadline__gte=timezone.now()).order_by('deadline').distinct()

    def get_safe_context(self, date_format):
        return {'name': self.name,
                'shortname': self.shortname,
                'url': settings.DOMAIN_FOR_URI + self.get_absolute_url(),
                }
        
@reversion.register(follow=('performance_set','roleinstance_set','showapplication_set','audition','techiead'))
class Show(DramaObjectModel):
    objects = ShowManager()
    book = models.URLField('Booking Link', blank=True)
    prices = models.CharField(max_length=30, blank=True)
    author = models.CharField(max_length=200, blank=True)
    societies = models.ManyToManyField(Society)
    image = models.ImageField(upload_to='images/', blank=True)
    has_applications = True

    class Meta:
        ordering = ['name']
        permissions = (
            ('approve_show', 'Approve Show'),
            )

    def __str__(self):
        return self.name

    def reslug(self):
        if self.performance_set.count() > 0:
            base_slug = slugify(str(self.opening_night.year) + '-' + self.name)
        else:
            base_slug = slugify(self.name)
        slug = base_slug
        if Show.objects.filter(slug=base_slug).exclude(id=self.id).count() > 0:
            for i in itertools.count(2):
                slug = slugify(base_slug + '-' + str(i))
                if Show.objects.filter(slug=slug).exclude(id=self.id).count() == 0:
                    break
        self.slug = slug
        self.group.name=self.slug
        self.group.save()
        self.save()

    reslug.alters_data=True

    @property
    def cast(self):
        return self.roleinstance_set.filter(role__cat='cast')

    @property
    def band(self):
        return self.roleinstance_set.filter(role__cat='band')

    @property
    def prod(self):
        return self.roleinstance_set.filter(role__cat='prod')

    @property
    def opening_night(self):
        try:
            return self.performance_set.order_by('start_date')[0].start_date
        except IndexError:
            return date(1973,7,24)

    @property
    def closing_night(self):
        try:
            return self.performance_set.order_by('-end_date')[0].end_date
        except IndexError:
            return date(1973,7,24)

    @property
    def dec_string(self):
        return '(' + self.opening_night.strftime('%b %Y') + ')'

    def get_applications(self):
        return ShowApplication.objects.filter(show=self)

    def get_company(self):
        return RoleInstance.objects.filter(show=self)
    
    def get_cast(self):
        return self.get_company().filter(role__cat='cast')

    def get_cast_list(self):
        cast = self.get_cast()
        if cast.count() == 0:
            return []
        elif cast.count == 1:
            return [(None, cast[0])]
        else:
            return [(None, cast[0])] + list(zip(cast[0:],cast[1:]))
    
    def get_band(self):
        return self.get_company().filter(role__cat='band')

    def get_band_list(self):
        band = self.get_band()
        if band.count() == 0:
            return []
        elif band.count == 1:
            return [(None, band[0])]
        else:
            return [(None, band[0])] + list(zip(band[0:],band[1:]))
    
    def get_prod(self):
        return self.get_company().filter(role__cat='prod')

    def get_prod_list(self):
        prod = self.get_prod()
        if prod.count() == 0:
            return []
        elif prod.count == 1:
            return [(None, prod[0])]
        else:
            return [(None, prod[0])] + list(zip(prod[0:],prod[1:]))

    def get_cast_form(self):
        return drama.forms.CastForm(prefix='cast')
        
    def get_band_form(self):
        return drama.forms.BandForm(prefix='band')

    def get_prod_form(self):
        return drama.forms.ProdForm(prefix='prod')
    
    def get_performances(self):
        return Performance.objects.filter(show=self)

    def get_auditions(self):
        return AuditionInstance.objects.filter(audition__show=self).filter(end_datetime__gte=timezone.now()).order_by('end_datetime', 'start_time').distinct()
    
    def get_apps(self):
        return ShowApplication.objects.filter(show=self).filter(deadline__gte=timezone.now()).order_by('deadline').distinct()

    def get_techiead(self):
        try:
            return TechieAd.objects.approved().filter(show=self).filter(deadline__gte=timezone.now()).order_by('deadline').distinct()[0]
        except IndexError:
            return None

    def get_remove_role_url(self):
        return self.get_url('remove-role')

    def get_role_reorder_url(self):
        return self.get_url('role-reorder')

    def get_safe_context(self, date_format):
        term, week = TermDate.get_label(self.opening_night)
        performances = []
        for perf in self.performance_set.all():
            performances.append(perf.get_safe_context(date_format))
        return {'name': self.name,
                'term': term,
                'week': week,
                'performances': performances,
                'url': settings.DOMAIN_FOR_URI + self.get_absolute_url(),
                }
    

class PerformanceInstance:
    def __init__(self, show, venue, start_datetime, end_datetime):
        self.show = show
        self.venue = venue
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
    def get_absolute_url(self):
        return self.show.get_absolute_url()


@reversion.register()
class Performance(models.Model):
    objects = ShowApprovedManager()

    def __str__(self):
        return "Performance of {} from {} to {} at {}".format(self.show.name, self.start_date, self.end_date, self.venue.name)
    show = models.ForeignKey(Show)
    start_date = models.DateField()
    end_date = models.DateField()
    time = models.TimeField()
    venue = models.ForeignKey(Venue)

    def get_performances(self):
        instances = []
        for i in range(0,self.performance_count()):
            date = self.start_date + timedelta(days=i)
            start_datetime = datetime.combine(date, self.time)
            end_datetime = start_datetime + timedelta(hours=2)
            instances.append(PerformanceInstance(show=self.show, venue=self.venue, start_datetime=start_datetime, end_datetime=end_datetime))
        return instances
            

    def performance_count(self, start_date=None, end_date=None):
        if end_date:
            end_date = min(end_date, self.end_date)
        else:
            end_date = self.end_date
        if start_date:
            start_date = max(start_date, self.start_date)
        else:
            start_date = self.start_date
        return (end_date - start_date).days + 1

    def get_safe_context(self, date_format):
        return {'start_date': defaultfilters.date(self.start_date, date_format),
                'end_date': defaultfilters.date(self.end_date, date_format),
                'time': defaultfilters.date(self.time, 'g:iA'),
                }


class Role(DramaObjectModel):
    objects = DramaObjectManager()
    categories = [
        ('cast', 'Cast'), ('band', 'Band'), ('prod', 'Production Team')]
    cat = models.CharField(
        max_length=4, choices=categories, verbose_name='Role Category')

    class Meta:
        ordering = ['name']
        permissions = (
            ('approve_role', 'Approve Role'),
            )

    def __str__(self):
        return self.name

    def get_vacancies(self):
        return TechieAd.objects.approved().filter(techieadrole__role=self).distinct()

    @property
    def dec_string(self):
        return ''
        

@reversion.register()
class RoleInstance(models.Model):
    objects = ShowApprovedManager()

    def __str__(self):
        return self.name + ' for ' + self.show.name
    name = models.CharField('Role name', max_length=200)
    show = models.ForeignKey(Show)
    person = models.ForeignKey(Person)
    role = models.ForeignKey(Role, verbose_name='Role Type')
    sort = models.IntegerField(default=1000)

    class Meta:
        ordering = ['sort']

    def get_link(self):
        """
        Get link text for the item, with appropriate <a> tag if the item is approved.
        """
        if self.role.approved:
            return mark_safe('<a href="{0}">{1}</a>'.format(self.role.get_absolute_url(), escape(self.name)))
        else:
            return self.name
        


@reversion.register(follow=('techieadrole_set',))
class TechieAd(models.Model):
    objects = AdvertManager()

    def __str__(self):
        return 'Tech ad for ' + self.show.name
    show = models.OneToOneField(Show)
    desc = models.TextField('Description', blank=True)
    contact = models.CharField(max_length=200)
    deadline = models.DateTimeField()
    def get_absolute_url(self):
        return self.show.get_absolute_url()
    def get_edit_url(self):
        return self.show.get_url('technical')
    def get_remove_url(self):
        return self.show.get_url('remove-technical')
    def can_edit(self, user):
        return user.has_perm('drama.change_show',self.show)
    def get_url(self):
        return reverse('techiead-item', kwargs={'slug': self.show.slug})
        
    def get_safe_context(self, date_format):
        positions = []
        for pos in self.techieadrole_set.all():
            positions.append(pos.get_safe_context(date_format))
        return {'show': self.show.get_safe_context(date_format),
                'positions': positions,
                'deadline_date': defaultfilters.date(self.deadline, date_format),
                'deadline_time': defaultfilters.date(self.deadline, 'g:iA'),
                'deadline': self.deadline,
                'description': self.desc,
                'contact': self.contact,
                'url': settings.DOMAIN_FOR_URI + self.get_url(),
                }


@reversion.register()
class TechieAdRole(models.Model):
    name = models.CharField(max_length=200)
    ad = models.ForeignKey(TechieAd)
    desc = models.TextField('Description', blank=True)
    role = models.ForeignKey(Role, verbose_name='Role Type')
    slug = models.SlugField(max_length=200, blank=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)
        super(TechieAdRole, self).save(*args, **kwargs)
    def get_safe_context(self, date_format):
        return {'name': self.name,
                }


@reversion.register(follow=('auditioninstance_set',))
class Audition(models.Model):
    objects = AdvertManager()
    show = models.OneToOneField(Show)
    desc = models.TextField('Description', blank=True)
    contact = models.CharField(max_length=200, blank=True)

    def get_absolute_url(self):
        return self.show.get_absolute_url()
    def get_edit_url(self):
        return self.show.get_url('auditions')
    def get_remove_url(self):
        return self.show.get_url('remove-auditions')
    def can_edit(self, user):
        return user.has_perm('drama.change_show',self.show)
    def get_url(self):
        return reverse('audition-item', kwargs={'slug': self.show.slug})

    def get_safe_context(self, date_format):
        sessions = []
        for ses in self.auditioninstance_set.all():
            sessions.append(ses.get_safe_context(date_format))
        return {'show': self.show.get_safe_context(date_format),
                'description': self.desc,
                'sessions': sessions,
                'contact': self.contact,
                'url': settings.DOMAIN_FOR_URI + self.get_url()
                }
                


@reversion.register()
class AuditionInstance(models.Model):
    objects = AuditionInstanceManager()
    audition = models.ForeignKey(Audition)
    end_datetime = models.DateTimeField()
    start_time = models.TimeField()
    location = models.CharField(max_length=200)
    def get_safe_context(self, date_format):
        return {'date': defaultfilters.date(self.end_datetime, date_format),
                'start_time': defaultfilters.date(self.start_time, 'g:iA'),
                'end_time': defaultfilters.date(self.end_datetime, 'g:iA'),
                'location': self.location,
                }

    @property
    def date(self):
        self.end_datetime.date()

    @property
    def end_time(self):
        self.end_datetime.time()


class Application(models.Model):
    name = models.CharField(max_length=200)
    desc = models.TextField('Description', blank=True)
    contact = models.CharField(max_length=200, blank=True)
    deadline = models.DateTimeField()
    slug = models.SlugField(
        max_length=200, blank=True, editable=False, unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.parent().name + '-' + self.name)
            if self.__class__.objects.filter(slug=base_slug).count() > 0:
                for i in itertools.count(2):
                    slug = slugify(base_slug + '-' + str(i))
                    if Show.objects.filter(slug=slug).count() == 0:
                        break
            else:
                slug = base_slug
            self.slug = slug
        return super(Application, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return self.parent().get_absolute_url()

    def get_url(self):
        return reverse('application-item', kwargs={'slug': self.slug})

    def get_safe_context(self, date_format):
        return {'name': self.name,
                'parent': self.parent().get_safe_context(date_format),
                'description': self.desc,
                'deadline_date': defaultfilters.date(self.deadline, date_format),
                'deadline_time': defaultfilters.date(self.deadline, 'g:iA'),
                'deadline': self.deadline,
                'url': settings.DOMAIN_FOR_URI + self.get_url(),
                } 


@reversion.register()
class ShowApplication(Application):
    objects = AdvertManager()
    show = models.ForeignKey(Show)

    def parent(self):
        return self.show

    @property
    def object_name(self):
        return self.show.name
    def can_edit(self, user):
        return user.has_perm('drama.change_show',self.show)
    def get_edit_url(self):
        return self.show.get_url('applications')
    def get_remove_url(self):
        return False


class SocietyApplication(Application):
    society = models.ForeignKey(Society)

    def parent(self):
        return self.society

    @property
    def object_name(self):
        return self.society.name
    def can_edit(self, user):
        return user.has_perm('drama.change_society',self.society)
    def get_edit_url(self):
        return self.society.get_url('applications')
    def get_remove_url(self):
        return False


class VenueApplication(Application):
    venue = models.ForeignKey(Venue)

    def parent(self):
        return self.venue

    @property
    def object_name(self):
        return self.venue.name
    def can_edit(self, user):
        return user.has_perm('drama.change_venue',self.venue)
    def get_edit_url(self):
        return self.venue.get_url('applications')
    def get_remove_url(self):
        return False

class PendingAdmin(models.Model):
    email = models.EmailField()
    show = models.ForeignKey(Show)

class PendingGroupMember(models.Model):
    email = models.EmailField()
    group = models.ForeignKey(auth.models.Group)

class TermDate(models.Model):
    YEAR_CHOICES = []
    for i in range(2000, (timezone.now().year + 2)):
        YEAR_CHOICES.append((i,i))

    MICH = 'MT'
    LENT = 'LT'
    EASTER = 'ET'
    CHRIST_VAC = 'CB'
    EASTER_VAC = 'EB'
    SUMMER_VAC = 'SB'
    TERM_CHOICES = (
        ('Terms', ((MICH, 'Michaelmas Term'),
                    (LENT, 'Lent Term'),
                    (EASTER, 'Easter Term'))),
        ('Breaks', ((CHRIST_VAC, 'Christmas Break'),
                    (EASTER_VAC, 'Easter Break'),
                    (SUMMER_VAC, 'Summer Break'))))
    
    year = models.IntegerField(choices=YEAR_CHOICES)
    term = models.CharField(max_length=2, choices=TERM_CHOICES)
    start = models.DateField()

    def __str__(self):
        return self.get_term_display() + ' ' + str(self.year)

    @classmethod
    def get_term(cls, date):
        try:
            return cls.objects.filter(start__lte=date).order_by('-start')[0]
        except IndexError:
            return None

    @classmethod
    def get_label(cls, date):
        term = cls.get_term(date)
        if term:
            week = math.floor((date - term.start)/timedelta(days=7))
            return (term.get_term_display() + ' ' + str(term.year), 'Week ' + str(week))
        else:
            return (None, None)


class LogItem(models.Model):
    CAT_CHOICES = [
        ('CREATE', 'Create'),
        ('EDIT', 'Edit'),
        ('APPROVE', 'Approval Change'),
        ('ADMIN', 'Admin Change'),
        ('DELETE', 'Delete'),
        ]
    cat = models.CharField('Type', max_length=10, choices=CAT_CHOICES)
    datetime = models.DateTimeField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    desc = models.TextField()

    def user_email(self):
        return self.user.email

    def object_link(self):
        return self.content_object.get_link_always()

class EmailList(DramaObjectModel):
    html_template = models.TextField()
    plaintext_template = models.TextField()
    default_address = models.EmailField()
    default_header = models.TextField()
    default_subject = models.CharField(max_length=256)
    from_addr = models.EmailField('From Address')
    date_format = models.CharField(max_length=50, default='D jS F Y')

    class Meta:
        permissions = (('view_emaillists', 'View Email Lists'),
                       ('approve_emaillist', 'Approve Email Lists'),
                       )

    def get_context(self, header):
        audition_objects = Audition.objects.approved().annotate(end_auditions=models.Max('auditioninstance__end_datetime')).filter(end_auditions__gte=timezone.now()).order_by('opening_night')
        auditions = []
        for aud in audition_objects:
            auditions.append(aud.get_safe_context(self.date_format))
        techiead_objects = TechieAd.objects.approved().filter(deadline__gte=timezone.now()).order_by('opening_night')
        techieads = []
        for tec in techiead_objects:
            techieads.append(tec.get_safe_context(self.date_format))
        applications = []
        venapp_objects = VenueApplication.objects.filter(venue__approved=True, deadline__gte=timezone.now()).order_by('deadline')
        for app in venapp_objects:
            applications.append(app.get_safe_context(self.date_format))
        socapp_objects = SocietyApplication.objects.filter(society__approved=True, deadline__gte=timezone.now()).order_by('deadline')
        for app in socapp_objects:
            applications.append(app.get_safe_context(self.date_format))
        showapp_objects = ShowApplication.objects.filter(deadline__gte=timezone.now()).order_by('opening_night', 'deadline')
        for app in showapp_objects:
            applications.append(app.get_safe_context(self.date_format))
        return {'auditions': auditions,
                'techieads': techieads,
                'applications': applications,
                'by_role': None, #TODO
                'header': header,
                }

    def render_html(self, header):
        return pystache.render(self.html_template, self.get_context(header))

    def render_plaintext(self, header):
        return pystache.render(self.plaintext_template, self.get_context(header))

    def send_message(self, address=None, subject=None, header=None):
        if not address:
            address = self.default_address
        if not header:
            header = self.default_header
        if not subject:
            subject = self.default_subject
        return send_mail(subject=subject, message=self.render_plaintext(header), from_email=self.from_addr,
                         recipient_list=[address], html_message=self.render_html(header))

    def get_form_handler_url(self):
        return self.get_url('form-handler') 

    def get_preview_html_url(self):
        return self.get_url('preview-html') 

    def get_preview_text_url(self):
        return self.get_url('preview-text') 

    def get_send_message_url(self):
        return self.get_url('send-message') 

    def get_absolute_url(self):
        return self.get_send_message_url()
