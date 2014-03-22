from drama.models import *
from django.views.generic import DetailView
from django.utils import timezone

def venue(self, **kwargs):
    context = super(DetailView, self).get_context_data(**kwargs)
    venue = context['object']
    context['shows'] = Show.objects.filter(performance__venue=venue).distinct()
    context['auditions'] = AuditionInstance.objects.filter(audition__show__performance__venue=venue).filter(end_datetime__gte=timezone.now()).order_by('end_datetime','start_time').distinct()
    context['techieads'] = TechieAd.objects.filter(show__performance__venue=venue).filter(deadline__gte=timezone.now()).order_by('deadline').distinct()
    context['showapps'] = ShowApplication.objects.filter(show__performance__venue=venue).filter(deadline__gte=timezone.now()).order_by('deadline')
    context['venueapps'] = VenueApplication.objects.filter(venue=venue).filter(deadline__gte=timezone.now()).order_by('deadline')
    context['current_pagetype']='venues'
    return context

def society(self, **kwargs):
    context = super(DetailView, self).get_context_data(**kwargs)
    society = context['object']
    context['shows'] = society.show_set
    context['auditions'] = AuditionInstance.objects.filter(audition__show__society=society).filter(end_datetime__gte=timezone.now()).order_by('end_datetime','start_time')
    context['techieads'] = TechieAd.objects.filter(show__society=society).filter(deadline__gte=timezone.now()).order_by('deadline')
    context['showapps'] = ShowApplication.objects.filter(show__society=society).filter(deadline__gte=timezone.now()).order_by('deadline')
    context['societyapps'] = SocietyApplication.objects.filter(society=society).filter(deadline__gte=timezone.now()).order_by('deadline')
    context['current_pagetype']='societies'
    return context
