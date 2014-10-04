from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils import timezone
from django_ical.views import ICalFeed
from drama.models import *
import itertools
import datetime

class AuditionFeed(Feed):
    title = 'Camdram.net auditions feed'
    link = reverse_lazy('auditions_feed')
    description = 'Student theatre auditions in Cambridge'
    description_template = 'drama/audition_feed.html'

    def items(self):
        aud_instances = AuditionInstance.objects.filter(end_datetime__gte=timezone.now()).order_by(
            'end_datetime', 'start_time').filter(audition__show__approved=True).select_related('audition')
        seen = set()
        seen_add = seen.add
        ads = [i.audition for i in aud_instances if i.audition.id not in seen and not seen_add(
            i.audition.id)]
        return ads

    def item_title(self, item):
        return item.show.name

    

class TechieAdFeed(Feed):
    title = 'Camdram.net production team vacancies'
    description = 'Technical theatre positions in Cambridge'
    link = reverse_lazy('techiead_feed')
    description_template = 'drama/techiead_feed.html'

    def items(self):
        return TechieAd.objects.filter(deadline__gte=timezone.now()).filter(show__approved=True).order_by('deadline')

    def item_title(self, item):
        return item.show.name

class ApplicationFeed(Feed):
    title = 'Camdram.net applications feed'
    description = 'Directing and producing oppourtunities in Cambridge'
    link = reverse_lazy('applications_feed')
    description_template = 'drama/application_feed.html'

    def items(self):
        showads = ShowApplication.objects.filter(
            deadline__gte=timezone.now()).filter(show__approved=True).order_by('deadline')
        socads = SocietyApplication.objects.filter(
            deadline__gte=timezone.now()).filter(society__approved=True).order_by('deadline')
        venueads = VenueApplication.objects.filter(
            deadline__gte=timezone.now()).filter(venue__approved=True).order_by('deadline')
        return itertools.chain(showads, socads, venueads)

    def item_title(self, item):
        return item.name

class RoleFeed(Feed):
    def get_object(self, request, *args, slug=None, **kwargs):
        return get_object_or_404(Role, slug=slug)

    def title(self, obj):
        return "Camdram.net {0} feed".format(obj.name)

    def link(self, obj):
        return reverse('role-feed',kwargs={'slug':obj.slug})

    def description(self, obj):
        return "Oppourtunities to be a {0} in Cambridge".format(obj.name)

    def items(self, obj):
        return obj.get_vacancies()

    def item_title(self, obj):
        return obj.show.name

    def item_description(self, obj):
        return obj.desc

class FullCal(ICalFeed):
    title = "Camdram.net iCal Feed"

    def items(self):
        return [item for x in Performance.objects.approved().filter(end_date__gte=timezone.now()) for item in x.get_performances()]

    def item_title(self,obj):
        return obj.show.name

    def item_start_datetime(self, obj):
        return obj.start_datetime

    def item_end_datetime(self, obj):
        return obj.end_datetime

    def item_location(self, obj):
        return obj.venue.name

    def item_geolocation(self, obj):
        return (obj.venue.lat, obj.venue.lng)

    
class SubCal(FullCal):
    def __init__(self, *args, model=None, **kwargs):
        self.model = model
        return super(SubCal, self).__init__(*args, **kwargs)

    def title(self, obj):
        return "Camdram.net iCal feed for {0}".format(str(obj))

    def get_object(self, request, *args, slug=None, **kwargs):
        return get_object_or_404(self.model, slug=slug)

    def items(self, obj):
        return [item for x in obj.get_performances().filter(end_date__gte=timezone.now()) for item in x.get_performances()]
