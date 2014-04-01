from drama.models import *
from drama.forms import *
from drama.views import MyDetailView
from django.views.generic import DetailView
from django.utils import timezone


def venue(self, **kwargs):
    context = super(MyDetailView, self).get_context_data(**kwargs)
    venue = context['object']
    context['shows'] = Show.objects.filter(performance__venue=venue).distinct()
    context['auditions'] = AuditionInstance.objects.filter(audition__show__performance__venue=venue).filter(
        end_datetime__gte=timezone.now()).order_by('end_datetime', 'start_time').distinct()
    try:
        context['auditions'][0]
    except IndexError:
        context['auditions'] = None

    context['techieads'] = TechieAd.objects.filter(show__performance__venue=venue).filter(
        deadline__gte=timezone.now()).order_by('deadline').distinct()
    try:
        context['techieads'][0]
    except IndexError:
        context['techieads'] = None

    context['showapps'] = ShowApplication.objects.filter(
        show__performance__venue=venue).filter(deadline__gte=timezone.now()).order_by('deadline').distinct()
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


def society(self, **kwargs):
    context = super(MyDetailView, self).get_context_data(**kwargs)
    society = context['object']
    context['shows'] = society.show_set
    context['auditions'] = AuditionInstance.objects.filter(audition__show__society=society).filter(
        end_datetime__gte=timezone.now()).order_by('end_datetime', 'start_time')
    try:
        context['auditions'][0]
    except IndexError:
        context['auditions'] = None

    context['techieads'] = TechieAd.objects.filter(show__society=society).filter(
        deadline__gte=timezone.now()).order_by('deadline')
    try:
        context['techieads'][0]
    except IndexError:
        context['techieads'] = None

    context['showapps'] = ShowApplication.objects.filter(
        show__society=society).filter(deadline__gte=timezone.now()).order_by('deadline')
    try:
        context['showapps'][0]
    except IndexError:
        context['showapps'] = None

    context['societyapps'] = SocietyApplication.objects.filter(
        society=society).filter(deadline__gte=timezone.now()).order_by('deadline')
    try:
        context['societyapps'][0]
    except IndexError:
        context['societyapps'] = None

    context['current_pagetype'] = 'societies'
    return context


def show(self, user, **kwargs):
    context = super(MyDetailView, self).get_context_data(**kwargs)
    show = context['object']
    context['can_edit'] = user.has_perm('drama.change_show', show)
    context['cast_form'] = CastForm()
    context['band_form'] = BandForm()
    context['prod_form'] = ProdForm()
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


def person(self, **kwargs):
    context = super(MyDetailView, self).get_context_data(**kwargs)
    person = context['object']
    roles = person.roleinstance_set.select_related('show__performace')
    past_roles = roles.exclude(show__performance__end_date__gte=timezone.now()).distinct()
    future_roles = roles.exclude(
        show__performance__start_date__lte=timezone.now()).distinct()
    current_roles = roles.filter(show__performance__start_date__lte=timezone.now()).filter(
        show__performance__end_date__gte=timezone.now).distinct()
    context = {'person': person, 'past_roles': past_roles,
               'current_roles': current_roles, 'future_roles': future_roles}
    return context

def role(self, **kwargs):
    context = super(MyDetailView, self).get_context_data(**kwargs)
    role = context['object']
    context['current_pagetype'] = 'roles'
    context['get_involved'] = TechieAd.objects.filter(techieadrole__role=role).distinct()
    return context
