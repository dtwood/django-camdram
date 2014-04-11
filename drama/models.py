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

class DramaObjectMixin(object):
    @classmethod
    def class_name(cls):
        return cls.__name__.lower()

    def get_url(self, action):
        return reverse(self.class_name() + '-' + action, kwargs={'slug': self.slug})
    
    def get_absolute_url(self):
        return reverse(self.class_name() + '-detail', kwargs={'slug': self.slug})

    def get_edit_url(self):
        return reverse(self.class_name() + '-edit', kwargs={'slug':self.slug})

    def get_remove_url(self):
        return reverse(self.class_name() + '-remove', kwargs={'slug':self.slug})

    @classmethod
    def get_list_url(cls):
        return reverse(cls.class_name() + '-list')

    def get_approve_url(self):
        return reverse(self.class_name() + '-approve', kwargs={'slug':self.slug})

    def get_unapprove_url(self):
        return reverse(self.class_name() + '-unapprove', kwargs={'slug':self.slug})

    def get_applications_url(self):
        return reverse(self.class_name() + '-applications', kwargs={'slug':self.slug})

    def get_admins_url(self):
        return reverse(self.class_name() + '-admins', kwargs={'slug':self.slug})

    def get_admin_revoke_url(self):
        return self.get_url('revoke-admin')
    
    def is_show(self):
        return False

    def has_applications(self):
        return False

    def get_link(self):
        """
        Get link text for the item, with appropriate <a> tag if the item is approved.
        """
        if self.approved:
            return mark_safe('<a href="{0}">{1}</a>'.format(self.get_absolute_url(), escape(self.name)))
        else:
            return self.name

    def approve(self):
        self.approved = True
        self.save()

    def unapprove(self):
        self.approved = False
        self.save()

    def get_detail_context(self, request):
        context = {}

class Person(models.Model, DramaObjectMixin):

    def __str__(self):
        return self.name
    name = models.CharField(max_length=200)
    desc = models.TextField('Bio', blank=True)
    slug = models.SlugField(max_length=200, blank=True, editable=False)
    approved = models.BooleanField(editable=False, default=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, editable=False, blank=True, null=True)

    class Meta:
        ordering = ['name']
        permissions = (
            ('approve_person', 'Approve Person'),
            )

    def save(self, *args, **kwargs):
        if not self.slug:
            temp_slug = slugify(self.name)
            if Person.objects.filter(slug=temp_slug):
                super(Person, self).save(*args, **kwargs)
                temp_slug = str(self.id) + '-' + temp_slug
            self.slug = temp_slug
        super(Person, self).save(*args, **kwargs)

    @property
    def num_shows(self):
        return Show.objects.filter(roleinstance__person=self).filter(approved=True).distinct().count()

    @property
    def first_active(self):
        try:
            return Performance.objects.filter(show__roleinstance__person=self).filter(show__approved=True).order_by('start_date')[0].start_date
        except IndexError:
            return None

    @property
    def last_active(self):
        try:
            return Performance.objects.filter(show__roleinstance__person=self).filter(show__approved=True).order_by('-end_date')[0].end_date
        except IndexError:
            return None

    @property
    def dec_string(self):
        if date.today() - self.last_active < timedelta(days=365):
            label = 'Active'
        else:
            label = 'Was Active: ' + \
                self.first_active.strftime('%b %y') + \
                ' - ' + self.last_active.strftime('%b %y')
        return '(' + label + ', Shows: ' + str(self.num_shows) + ')'

    def get_cname(*args):
        return "people"

    def get_detail_context(self, request):
        context = {}
        person = self
        roles = person.roleinstance_set.select_related('show__performace').filter(show__approved=True)
        past_roles = roles.exclude(show__performance__end_date__gte=timezone.now()).distinct()
        future_roles = roles.exclude(show__performance__start_date__lte=timezone.now()).distinct()
        current_roles = roles.filter(show__performance__start_date__lte=timezone.now()).filter(show__performance__end_date__gte=timezone.now).distinct()
        context = {'person': person, 'past_roles': past_roles,
                'current_roles': current_roles, 'future_roles': future_roles}
        return context
        
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


class Venue(models.Model, DramaObjectMixin):

    def __str__(self):
        return self.name
    name = models.CharField(max_length=200)
    desc = models.TextField('Description', blank=True)
    address = models.CharField(max_length=200, blank=True)
    slug = models.SlugField(max_length=200, blank=True, editable=False)
    approved = models.BooleanField(editable=False, default=False)
    group = models.OneToOneField(auth.models.Group, null=True, blank=True, editable=False)

    class Meta:
        ordering = ['name']
        permissions = (
            ('approve_venue', 'Approve Venue'),
            ('admin_venue', 'Change venue admins'),
            )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.group:
            new_group = auth.models.Group(name=self.name)
            new_group.save()
            self.group = new_group
        super(Venue, self).save(*args, **kwargs)

    @property
    def dec_string(self):
        return ''

    def get_cname(*args):
        return "venues"

    def get_applications(self):
        return VenueApplication.objects.filter(venue=self)

    def has_applications(self):
        return True

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
        Add the user with this email address to the venue admins.
        If the user does not exist, add the request to the pending admins list.
        """
        try:
            user = auth.get_user_model().objects.filter(email=email)[0]
            self.group.user_set.add(user)
        except IndexError:
            item = PendingGroupMember(email=email, group=self.group)
            item.save()
    def remove_admin(self, username):
        """
        Remove the user with that username from the venue admins.
        """
        try:
            user = auth.get_user_model().objects.filter(username=username)[0]
            self.group.user_set.remove(user)
        except IndexError:
            pass

    def get_detail_context(self, request):
        venue = self
        context = {}
        context['shows'] = Show.objects.filter(performance__venue=venue).filter(approved=True).distinct()
        context['auditions'] = AuditionInstance.objects.filter(audition__show__performance__venue=venue).filter(
        end_datetime__gte=timezone.now()).filter(audition__show__approved=True).order_by('end_datetime', 'start_time').distinct()
        try:
            context['auditions'][0]
        except IndexError:
            context['auditions'] = None

        context['techieads'] = TechieAd.objects.filter(show__performance__venue=venue).filter(show__approved=True).filter(
            deadline__gte=timezone.now()).order_by('deadline').distinct()
        try:
            context['techieads'][0]
        except IndexError:
            context['techieads'] = None

        context['showapps'] = ShowApplication.objects.filter(
            show__performance__venue=venue).filter(deadline__gte=timezone.now()).filter(show__approved=True).order_by('deadline').distinct()
        try:
            context['showapps'][0]
        except IndexError:
            context['showapps'] = None

        context['venueapps'] = VenueApplication.objects.filter(
            venue=venue).filter(deadline__gte=timezone.now()).order_by('deadline')
        try:
            context['venueapps'][0]
        except IndexError:
            context['venueapps'] = None

        context['current_pagetype'] = 'venues'
        return context

class Society(models.Model, DramaObjectMixin):

    def __str__(self):
        return self.name
    name = models.CharField(max_length=200)
    shortname = models.CharField(max_length=100, verbose_name="Abbreviaiton")
    desc = models.TextField('Description', blank=True)
    image = models.ImageField(
        upload_to='images/', blank=True, verbose_name="Logo")
    slug = models.SlugField(max_length=200, blank=True, editable=False)
    approved = models.BooleanField(editable=False, default=False)
    group = models.OneToOneField(auth.models.Group, null=True, blank=True, editable=False)

    class Meta:
        ordering = ['name']
        permissions = (
            ('approve_society', 'Approve Society'),
            ('admin_society', 'Change society admins'),
            )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.group:
            new_group = auth.models.Group(name=self.name)
            new_group.save()
            self.group = new_group
        super(Society, self).save(*args, **kwargs)

    @property
    def dec_string(self):
        return ''

    def get_cname(*args):
        return "societies"

    def get_applications(self):
        return SocietyApplication.objects.filter(society=self)
    
    def has_applications(self):
        return True

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
        Add the user with this email address to the society admins.
        If the user does not exist, add the request to the pending admins list.
        """
        try:
            user = auth.get_user_model().objects.filter(email=email)[0]
            self.group.user_set.add(user)
        except IndexError:
            item = PendingGroupMember(email=email, group=self.group)
            item.save()

    def remove_admin(self, username):
        """
        Remove the user with that username from the society admins.
        """
        try:
            user = auth.get_user_model().objects.filter(username=username)[0]
            self.group.user_set.remove(user)
        except IndexError:
            pass
        
    def get_detail_context(self, request):
        society = self
        context = {}    
        context['shows'] = society.show_set.filter(approved=True)
        context['auditions'] = AuditionInstance.objects.filter(audition__show__society=society).filter(end_datetime__gte=timezone.now()).filter(audition__show__approved=True).order_by('end_datetime', 'start_time')
        try:
            context['auditions'][0]
        except IndexError:
            context['auditions'] = None
    
        context['techieads'] = TechieAd.objects.filter(show__society=society).filter(deadline__gte=timezone.now()).filter(show__approved=True).order_by('deadline')
        try:
            context['techieads'][0]
        except IndexError:
            context['techieads'] = None
    
        context['showapps'] = ShowApplication.objects.filter(show__society=society).filter(deadline__gte=timezone.now()).filter(show__approved=True).order_by('deadline')
        try:
            context['showapps'][0]
        except IndexError:
            context['showapps'] = None
    
        context['societyapps'] = SocietyApplication.objects.filter(society=society).filter(deadline__gte=timezone.now()).order_by('deadline')
        try:
            context['societyapps'][0]
        except IndexError:
            context['societyapps'] = None
    
        context['current_pagetype'] = 'societies'
        return context


class Show(models.Model, DramaObjectMixin):

    def __str__(self):
        return self.name
    name = models.CharField(max_length=200)
    desc = models.TextField('Description', blank=True)
    book = models.URLField('Booking Link', blank=True)
    prices = models.CharField(max_length=30, blank=True)
    author = models.CharField(max_length=200, blank=True)
    society = models.ForeignKey(Society)
    year = models.IntegerField()
    image = models.ImageField(upload_to='images/', blank=True)
    slug = models.SlugField(max_length=200, blank=True, unique=True)
    approved = models.BooleanField(editable=False, default=False)

    class Meta:
        ordering = ['name']
        permissions = (
            ('approve_show', 'Approve Show'),
            ('admin_show', 'Change show admins'),
            )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(str(self.year) + '-' + self.name)
        try:
            super(Show, self).save(*args, **kwargs)
        except IntegrityError:
            self.slug = slugify(self.slug + '-' + self.id)
            super(Show, self).save(*args, **kwargs)

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
            return date(self.year, 1, 1)

    @property
    def closing_night(self):
        try:
            return self.performance_set.order_by('-end_date')[0].end_date
        except IndexError:
            return date(self.year, 1, 1)

    @property
    def dec_string(self):
        return '(' + self.opening_night.strftime('%b %Y') + ')'

    def get_cname(*args):
        return "shows"

    def get_applications(self):
        return ShowApplication.objects.filter(show=self)

    def is_show(self):
        return True

    def has_applications(self):
        return True

    def get_link(self):
        """
        Always return link, so show admin works.
        """
        return mark_safe('<a href="{0}">{1}</a>'.format(self.get_absolute_url(), escape(self.name)))

    def get_admins(self):
        """
        Return the current admins.
        """
        return get_users_with_perms(self, with_group_users=False)

    def get_pending_admins(self):
        """
        return the pending admins
        """
        return self.pendingadmin_set.all()
    
    def add_admin(self, email):
        """
        Add the user with this email address to the shows admins.
        If the user does not exist, add the request to the pending admins list.
        """
        try:
            user = auth.get_user_model().objects.filter(email=email)[0]
            assign_perm('drama.change_show', user, self)
        except IndexError:
            item = PendingAdmin(email=email, show=self)
            item.save()

    def remove_admin(self, username):
        """
        Remove the user with that username from the show admins.
        """
        try:
            user = auth.get_user_model().objects.filter(username=username)[0]
            remove_perm('change_show', user, self)
        except IndexError:
            pass

    def get_detail_context(self, request):
        context = {}
        show = self
        context['can_edit'] = request.user.has_perm('drama.change_show', show)
        from drama import forms
        context['cast_form'] = forms.CastForm()
        context['band_form'] = forms.BandForm()
        context['prod_form'] = forms.ProdForm()
        company = RoleInstance.objects.filter(show=show)
        cast = company.filter(role__cat='cast')
        if cast.count() == 0:
            context['cast'] = []
        elif cast.count() == 1:
            context['cast'] = [(None, cast[0])]
        else:
            context['cast'] = [(None, cast[0])] + list(zip(cast[0:],cast[1:]))
        band = company.filter(role__cat='band')
        if band.count() == 0:
            context['band'] = []
        elif band.count() == 1:
            context['band'] = [(None, band[0])]
        else:
            context['band'] = [(None, band[0])] + list(zip(band[0:],band[1:]))
        prod = company.filter(role__cat='prod')
        if prod.count() == 0:
            context['prod'] = []
        elif prod.count() == 1:
            context['prod'] = [(None, prod[0])]
        else:
            context['prod'] = [(None, prod[0])] + list(zip(prod[0:],prod[1:]))
        context['performances'] = show.performance_set.all()
        context['auditions'] = AuditionInstance.objects.filter(audition__show=show).filter(
            end_datetime__gte=timezone.now()).order_by('end_datetime', 'start_time')
        try:
            context['auditions'][0]
        except IndexError:
            context['auditions'] = None
    
        context['applications'] = ShowApplication.objects.filter(
            show=show).filter(deadline__gte=timezone.now()).order_by('deadline')
        try:
            context['applications'][0]
        except IndexError:
            context['applications'] = None
    
        try:
            context['techiead'] = TechieAd.objects.filter(show=show).get()
        except TechieAd.DoesNotExist:
            pass
        return context
        


class Performance(models.Model):

    def __str__(self):
        return "Performance of {} from {} to {} at {}".format(self.show.name, self.start_date, self.end_date, self.venue.name)
    show = models.ForeignKey(Show)
    start_date = models.DateField()
    end_date = models.DateField()
    time = models.TimeField()
    venue = models.ForeignKey(Venue)

    def get_cname(*args):
        return "performances"


class Role(models.Model, DramaObjectMixin):

    def __str__(self):
        return self.name
    name = models.CharField(max_length=200)
    desc = models.TextField('Description', blank=True)
    categories = [
        ('cast', 'Cast'), ('band', 'Band'), ('prod', 'Production Team')]
    cat = models.CharField(
        max_length=4, choices=categories, verbose_name='Role Category')
    slug = models.SlugField(max_length=200, blank=True, editable=False)
    approved = models.BooleanField(editable=False, default=False)

    class Meta:
        ordering = ['name']
        permissions = (
            ('approve_role', 'Approve Role'),
            ('admin_role', 'Change role admins'),
            )

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)
        super(Role, self).save(*args, **kwargs)

    def get_cname(*args):
        return "roles"

    def get_detail_context(self, request):
        context = {}
        context['current_pagetype'] = 'roles'
        context['get_involved'] = TechieAd.objects.filter(techieadrole__role=self).filter(show__approved=True).distinct()
        return context
        

class RoleInstance(models.Model):

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
        


class TechieAd(models.Model):

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

    def get_cname(*args):
        return "techieadroles"


class Audition(models.Model):
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


class AuditionInstance(models.Model):
    audition = models.ForeignKey(Audition)
    end_datetime = models.DateTimeField()

    @property
    def date(self):
        self.start_datetime.date()

    @property
    def end_time(self):
        self.start_datetime.time()
    start_time = models.TimeField()
    location = models.CharField(max_length=200)
    def get_cname(*args):
        return "audition session"


class Application(models.Model):
    name = models.CharField(max_length=200)
    desc = models.TextField('Description', blank=True)
    contact = models.CharField(max_length=200, blank=True)
    deadline = models.DateTimeField()
    slug = models.SlugField(
        max_length=200, blank=True, editable=False, unique=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.object_name + '-' + self.name)
        try:
            super(Application, self).save(*args, **kwargs)
        except IntegrityError:
            self.slug = slugify(self.id + '-' + self.slug)
            super(Application, self).save(*args, **kwargs)


class ShowApplication(Application):
    show = models.ForeignKey(Show)

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

    @property
    def object_name(self):
        return self.society.name
    def can_edit(self, user):
        return user.has_perm('drama.change_society',self.society)
    def get_edit_url(self):
        return self.venue.get_url('applications')
    def get_remove_url(self):
        return False


class VenueApplication(Application):
    venue = models.ForeignKey(Venue)

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
