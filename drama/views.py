from django.shortcuts import render, get_object_or_404
from drama.models import *
from django.utils import timezone
from django.http import HttpResponse

def index(request):
    return HttpResponse("Hello World")

def show(request,slug):
    show = get_object_or_404(Show,slug=slug)
    company = RoleInstance.objects.filter(show=show)
    cast = company.filter(role__cat='cast')
    band = company.filter(role__cat='band')
    prod = company.filter(role__cat='prod')
    performances = Performance.objects.filter(show=show)
    context = {'show': show, 'cast': cast, 'band': band, 'prod': prod, 'performances': performances}
    return render(request, 'drama/show.html', context)

def person(request,slug):
    person = get_object_or_404(Person,slug=slug)
    roles = RoleInstance.objects.filter(person=person)
    past_roles = roles.exclude(show__performance__end_date__gte=timezone.now())
    future_roles = roles.exclude(show__performance__start_date__lte=timezone.now())
    current_roles = roles.filter(show__performance__start_date__lte=timezone.now()).filter(show__performance__end_date__gte=timezone.now)
    context = {'person': person, 'past_roles':past_roles, 'current_roles':current_roles, 'future_roles': future_roles}
    return render(request, 'drama/person.html', context)

def society(request,slug):
    return HttpResponse("Hello World")

def venue(request,slug):
    return HttpResponse("Hello World")

def role(request,slug):
    return HttpResponse("Hello World")

def auditions(request):
    return HttpResponse("Hello World")

def applications(request):
    return HttpResponse("Hello World")

def ad_role(request, show_slug, role_slug):
    role = get_object_or_404(TechieAdRole,slug=role_slug,ad__show__slug=show_slug)
    context = {'role':role, 'current_roletype':'', 'current_pagetype':'vacancies'}
    return render(request, 'drama/ad_role.html', context)

def techieads(request):
    ads = TechieAd.objects.all()
    context = {'ads': ads, 'current_roletype':'techie', 'current_pagetype':'vacancies'}
    return render(request, 'drama/techiead.html', context)
