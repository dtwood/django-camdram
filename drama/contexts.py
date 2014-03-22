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

def show(self, **kwargs):
    context = super(DetailView, self).get_context_data(**kwargs)
    show = context['object']
    company = RoleInstance.objects.filter(show=show)
    context['cast'] = company.filter(role__cat='cast')
    context['band'] = company.filter(role__cat='band')
    context['prod'] = company.filter(role__cat='prod')
    context['performances'] = show.performance_set.all()
    context['auditions'] = AuditionInstance.objects.filter(audition__show=show).filter(end_datetime__gte=timezone.now()).order_by('end_datetime','start_time')
    context['applications'] = ShowApplication.objects.filter(show=show).filter(deadline__gte=timezone.now()).order_by('deadline')
    try:
        context['techiead'] = TechieAd.objects.filter(show=show).get()
    except TechieAd.DoesNotExist:
        pass
    return context

def person(self, **kwargs):
    context = super(DetailView, self).get_context_data(**kwargs)
    person = context['object']
    roles = person.roleinstance_set.select_related('show__performace')
    past_roles = roles.exclude(show__performance__end_date__gte=timezone.now())
    future_roles = roles.exclude(show__performance__start_date__lte=timezone.now())
    current_roles = roles.filter(show__performance__start_date__lte=timezone.now()).filter(show__performance__end_date__gte=timezone.now)
    context = {'person': person, 'past_roles':past_roles, 'current_roles':current_roles, 'future_roles': future_roles}
    return context
