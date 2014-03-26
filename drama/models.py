from django.db import models, IntegrityError
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
from datetime import date, timedelta, datetime

class Person(models.Model):
    def __str__(self): return self.name
    name = models.CharField(max_length=200)
    desc = models.TextField('Bio', blank=True)
    slug = models.SlugField(max_length=200, blank=True, editable=False)
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
        return self.show_set.distinct().count()
    @property
    def first_active(self):
        try:
            return Performance.objects.filter(show__roleinstance__person=self).order_by('start_date')[0].start_date
        except IndexError:
            return None
    @property
    def last_active(self):
        try:
            return Performance.objects.filter(show__roleinstance__person=self).order_by('-end_date')[0].end_date
        except IndexError:
            return None
    @property
    def dec_string(self):
        if date.today() - self.last_active < timedelta(days=365):
            label = 'Active'
        else:
            label = 'Was Active: ' + self.first_active.strftime('%b %y') + ' - ' + self.last_active.strftime('%b %y')
        return '(' + label + ', Shows: ' + str(self.num_shows) + ')'
    def get_cname(*args):
        return "people"
    
    #TODO: Link to account
    #account = models.ForeignKey(accounts.Account)

class Venue(models.Model):
    def __str__(self): return self.name
    name = models.CharField(max_length=200)
    desc = models.TextField('Description', blank=True)
    address = models.CharField(max_length=200, blank=True)
    slug = models.SlugField(max_length=200, blank=True, editable=False)
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Venue, self).save(*args, **kwargs)
    @property
    def dec_string(self):
        return ''
    def get_cname(*args):
        return "venues"
    #TODO: Adress

class Society(models.Model):
    def __str__(self): return self.name
    name = models.CharField(max_length=200)
    shortname = models.CharField(max_length=100,verbose_name="Abbreviaiton")
    desc = models.TextField('Description', blank=True)
    image = models.ImageField(upload_to='images/', blank=True, verbose_name="Logo")
    slug = models.SlugField(max_length=200, blank=True, editable=False)
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Society, self).save(*args, **kwargs)
    def get_absolute_url(self):
        return reverse('display',kwargs={'model_name':'societies','slug':self.slug})
    @property
    def dec_string(self):
        return ''
    def get_cname(*args):
        return "societies"

class Show(models.Model):
    def __str__(self): return self.name
    name = models.CharField(max_length=200)
    desc = models.TextField('Description', blank=True)
    book = models.URLField('Booking Link', blank=True)
    prices = models.TextField(blank=True)
    author = models.CharField(max_length=200,blank=True)
    society = models.ForeignKey(Society)
    year = models.IntegerField()
    image = models.ImageField(upload_to='images/',blank=True)
    slug = models.SlugField(max_length=200, blank=True, unique=True)
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(str(self.year) + '-' + self.name)
        try:
            super(Show, self).save(*args, **kwargs)
        except IntegrityError:
            self.slug = slugify(self.slug + '-' + self.id)
            super(Show, self).save(*args, **kwargs)
            
    @property
    def opening_night(self):
        try:
            return self.performance_set.order_by('start_date')[0].start_date
        except IndexError:
            return date(self.year,1,1)
    @property
    def closing_night(self):
        try:
            return self.performance_set.order_by('-end_date')[0].end_date
        except IndexError:
            return date(self.year,1,1)
    @property
    def dec_string(self):
        return '('+self.opening_night.strftime('%b %Y')+')'
    def get_cname(*args):
        return "shows"
    def get_absolute_url(self):
        return reverse('display',kwargs={'model_name':'shows','slug':self.slug})

class Performance(models.Model):
    def __str__(self):
        return "Performance of {} from {} to {} at {}".format(self.show.name,self.start_date,self.end_date,self.venue.name)
    show = models.ForeignKey(Show)
    start_date = models.DateField()
    end_date = models.DateField()
    time = models.TimeField()
    venue = models.ForeignKey(Venue)
    def get_cname(*args):
        return "performances"
    
class Role(models.Model):
    def __str__(self): return self.name
    name = models.CharField(max_length=200)
    desc = models.TextField('Description', blank=True)
    categories = [('cast', 'Cast'), ('band', 'Band'), ('prod', 'Production Team')]
    cat = models.CharField(max_length=4,choices=categories, verbose_name='Role Category')
    link = models.BooleanField()
    slug = models.SlugField(max_length=200, blank=True, editable=False)
    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)
        super(Role, self).save(*args, **kwargs)

class RoleInstance(models.Model):
    def __str__(self): return self.name + ' for ' + self.show.name
    name = models.CharField('Role name', max_length=200)
    show = models.ForeignKey(Show)
    person = models.ForeignKey(Person)
    role = models.ForeignKey(Role, verbose_name='Role Type')

class TechieAd(models.Model):
    def __str__(self): return 'Tech ad for ' + self.show.name
    show = models.OneToOneField(Show)
    desc = models.TextField('Description', blank=True)
    contact = models.CharField(max_length=200)
    deadline = models.DateTimeField()

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

class Audition(models.Model):
    show = models.OneToOneField(Show)
    desc = models.TextField('Description', blank=True)
    contact = models.CharField(max_length=200, blank=True)
    @property
    def starts_at(self):
        try:
            first = self.auditioninstance_set.order_by('date','start_time')[0]
            return datetime.combine(first.date,first.start_time)
        except IndexError:
            return None

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

class Application(models.Model):
    name = models.CharField(max_length=200)
    desc = models.TextField('Description', blank=True)
    contact = models.CharField(max_length=200, blank=True)
    deadline = models.DateTimeField()
    slug = models.SlugField(max_length=200, blank=True, editable=False, unique=True)
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

class SocietyApplication(Application):
    society = models.ForeignKey(Society)
    @property
    def object_name(self):
        return self.society.name

class VenueApplication(Application):
    venue = models.ForeignKey(Venue)
    @property
    def object_name(self):
        return self.venue.name

