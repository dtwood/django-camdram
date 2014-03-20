from django.db import models
from django.template.defaultfilters import slugify

class Person(models.Model):
    def __str__(self): return self.name
    name = models.CharField(max_length=200)
    desc = models.TextField('Bio', blank=True)
    slug = models.SlugField(max_length=200, blank=True, editable=False)
    def save(self, *args, **kwargs):
        if not self.id:
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
            return self.show_set.performance_set.order_by('start_date')[0].start_date
        except IndexError:
            return None
    @property
    def last_active(self):
        try:
            return self.show_set.performance_set.order_by('-end_date')[0].end_date
        except IndexError:
            return None
    
    #TODO: Link to account
    #account = models.ForeignKey(accounts.Account)

class Venue(models.Model):
    def __str__(self): return self.name
    name = models.CharField(max_length=200)
    desc = models.TextField('Description', blank=True)
    address = models.CharField(max_length=200, blank=True)
    slug = models.SlugField(max_length=200, blank=True, editable=False)
    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)
        super(Venue, self).save(*args, **kwargs)
    #TODO: Adress

class Society(models.Model):
    def __str__(self): return self.name
    name = models.CharField(max_length=200)
    shortname = models.CharField(max_length=100,verbose_name="Abbreviaiton")
    desc = models.TextField('Description', blank=True)
    slug = models.SlugField(max_length=200, blank=True, editable=False)
    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)
        super(Society, self).save(*args, **kwargs)

class Show(models.Model):
    def __str__(self): return self.name
    name = models.CharField(max_length=200)
    desc = models.TextField('Description', blank=True)
    book = models.URLField('Booking Link', blank=True)
    prices = models.TextField(blank=True)
    company = models.ManyToManyField(Person, through='RoleInstance',verbose_name='Role')
    author = models.CharField(max_length=200,blank=True)
    society = models.ForeignKey(Society)
    year = models.IntegerField()
    image = models.ImageField(upload_to='images/',blank=True)
    slug = models.SlugField(max_length=200, blank=True)
    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(str(self.year) + '-' + self.name)
        super(Show, self).save(*args, **kwargs)
    @property
    def opening_night(self):
        try:
            return self.performance_set.order_by('start_date')[0].start_date
        except IndexError:
            return None
    @property
    def closing_night(self):
        try:
            return self.performance_set.order_by('-end_date')[0].end_date
        except IndexError:
            return None

class Performance(models.Model):
    def __str__(self):
        return "Performance of {} from {} to {} at {}".format(self.show.name,self.start_date,self.end_date,self.venue.name)
    show = models.ForeignKey(Show)
    start_date = models.DateField()
    end_date = models.DateField()
    time = models.TimeField()
    venue = models.ForeignKey(Venue)
    
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

class AuditionInstance(models.Model):
    audition = models.ForeignKey(Audition)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length=200)

class ShowApplication(models.Model):
    show = models.ForeignKey(Show)
    name = models.CharField(max_length=200)
    desc = models.TextField('Description', blank=True)
    contact = models.CharField(max_length=200, blank=True)
    deadline = models.DateTimeField()
    slug = models.SlugField(max_length=200, blank=True, editable=False)
    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)
        super(ShowApplication, self).save(*args, **kwargs)

class SocietyApplication(models.Model):
    society = models.ForeignKey(Society)
    name = models.CharField(max_length=200)
    desc = models.TextField('Description', blank=True)
    contact = models.CharField(max_length=200, blank=True)
    deadline = models.DateTimeField()
    slug = models.SlugField(max_length=200, blank=True, editable=False)
    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)
        super(SocietyApplication, self).save(*args, **kwargs)

class VenueApplication(models.Model):
    venue = models.ForeignKey(Venue)
    name = models.CharField(max_length=200)
    desc = models.TextField('Description', blank=True)
    contact = models.CharField(max_length=200, blank=True)
    deadline = models.DateTimeField()
    slug = models.SlugField(max_length=200, blank=True, editable=False)
    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)
        super(VenueApplication, self).save(*args, **kwargs)

