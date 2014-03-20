from django.shortcuts import render, get_object_or_404, redirect
from drama.models import *
from django.utils import timezone
from django.http import HttpResponse
from django.core.urlresolvers import reverse

def index(request):
    return HttpResponse("Hello World")

def show(request,slug):
    show = get_object_or_404(Show,slug=slug)
    company = RoleInstance.objects.filter(show=show)
    cast = company.filter(role__cat='cast')
    band = company.filter(role__cat='band')
    prod = company.filter(role__cat='prod')
    performances = show.performance_set.all()
    context = {'show': show, 'cast': cast, 'band': band, 'prod': prod, 'performances': performances}
    return render(request, 'drama/show.html', context)

def person(request,slug):
    person = get_object_or_404(Person,slug=slug)
    roles = person.roleinstance_set.select_related(show__performace)
    past_roles = roles.exclude(show__performance__end_date__gte=timezone.now())
    future_roles = roles.exclude(show__performance__start_date__lte=timezone.now())
    current_roles = roles.filter(show__performance__start_date__lte=timezone.now()).filter(show__performance__end_date__gte=timezone.now)
    context = {'person': person, 'past_roles':past_roles, 'current_roles':current_roles, 'future_roles': future_roles}
    return render(request, 'drama/person.html', context)

def society(request,slug):
    society = get_object_or_404(Society,slug=slug)
    shows = society.show_set
    auditions = AuditionInstance.objects.filter(audition__show__society=society).filter(date__gte=timezone.now()).order_by('date','start_time','end_time')
    techieads = TechieAd.objects.filter(show__society=society).filter(deadline__gte=timezone.now()).order_by('deadline')
    showapps = ShowApplication.objects.filter(show__society=society).filter(deadline__gte=timezone.now()).order_by('deadline')
    societyapps = SocietyApplication.objects.filter(society=society).filter(deadline__gte=timezone.now()).order_by('deadline')
    
    context = {'society':society, 'shows':shows, 'auditions':auditions, 'techieads':techieads, 'showapps':showapps, 'societyapps':societyapps}
    return render(request, 'drama/society.html', context)

def societies(request):
    return HttpResponse("Hello World")

def venue(request,slug):
    venue = get_object_or_404(Venue,slug=slug)
    shows = Show.objects.filter(performance__venue=venue).distinct()
    auditions = AuditionInstance.objects.filter(audition__show__performance__venue=venue).filter(date__gte=timezone.now()).order_by('date','start_time','end_time').distinct()
    techieads = TechieAd.objects.filter(show__performance__venue=venue).filter(deadline__gte=timezone.now()).order_by('deadline').distinct()
    showapps = ShowApplication.objects.filter(show__performance__venue=venue).filter(deadline__gte=timezone.now()).order_by('deadline')
    venueapps = VenueApplication.objects.filter(venue=venue).filter(deadline__gte=timezone.now()).order_by('deadline')
    context = {'venue':venue, 'shows':shows, 'auditions':auditions, 'techieads':techieads, 'showapps':showapps, 'venueapps':venueapps}
    return render(request, 'drama/venue.html', context)

def venues(request):
    return HttpResponse("Hello World")

def role(request,slug):
    return HttpResponse("Hello World")

def auditions(request):
    return HttpResponse("Hello World")

def auditions_item(request,slug):
    return redirect(reverse('auditions') + '#' + slug)

def applications(request):
    return HttpResponse("Hello World")

def applications_item(request,slug):
    return redirect(reverse('applications') + '#' + slug)

def ad_role(request, show_slug, role_slug):
    role = get_object_or_404(TechieAdRole,slug=role_slug,ad__show__slug=show_slug)
    context = {'role':role, 'current_roletype':'', 'current_pagetype':'vacancies'}
    return render(request, 'drama/ad_role.html', context)

def techieads(request):
    ads = TechieAd.objects.filter(deadline__gte=timezone.now()).order_by('deadline')
    context = {'ads': ads, 'current_roletype':'techie', 'current_pagetype':'vacancies'}
    return render(request, 'drama/techiead.html', context)

def techieads_item(request,slug):
    return redirect(reverse('techie_ads') + '#' + slug)

