from django.shortcuts import render, get_object_or_404, redirect
from drama.models import *
from django.utils import timezone
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from haystack.query import SearchQuerySet
import json

def index(request):
    return HttpResponse("Hello World")

def diary(request):
    return HttpResponse("Hello World")

def show(request,slug):
    show = get_object_or_404(Show,slug=slug)
    company = RoleInstance.objects.filter(show=show)
    cast = company.filter(role__cat='cast')
    band = company.filter(role__cat='band')
    prod = company.filter(role__cat='prod')
    performances = show.performance_set.all()
    auditions = AuditionInstance.objects.filter(audition__show=show).filter(end_datetime__gte=timezone.now()).order_by('end_datetime','start_time')
    applications = ShowApplication.objects.filter(show=show).filter(deadline__gte=timezone.now()).order_by('deadline')
    try:
        techiead = TechieAd.objects.filter(show=show).get()
    except TechieAd.DoesNotExist:
        techiead = None
    context = {'show': show, 'cast': cast, 'band': band, 'prod': prod, 'performances': performances, 'applications':applications, 'auditions':auditions, 'techiead':techiead}
    return render(request, 'drama/show.html', context)

def person(request,slug):
    person = get_object_or_404(Person,slug=slug)
    roles = person.roleinstance_set.select_related('show__performace')
    past_roles = roles.exclude(show__performance__end_date__gte=timezone.now()).order_by('-closing_night')
    future_roles = roles.exclude(show__performance__start_date__lte=timezone.now()).order_by('opening_night')
    current_roles = roles.filter(show__performance__start_date__lte=timezone.now()).filter(show__performance__end_date__gte=timezone.now)
    context = {'person': person, 'past_roles':past_roles, 'current_roles':current_roles, 'future_roles': future_roles}
    return render(request, 'drama/person.html', context)

def society(request,slug):
    society = get_object_or_404(Society,slug=slug)
    shows = society.show_set
    auditions = AuditionInstance.objects.filter(audition__show__society=society).filter(end_datetime__gte=timezone.now()).order_by('end_datetime','start_time')
    techieads = TechieAd.objects.filter(show__society=society).filter(deadline__gte=timezone.now()).order_by('deadline')
    showapps = ShowApplication.objects.filter(show__society=society).filter(deadline__gte=timezone.now()).order_by('deadline')
    societyapps = SocietyApplication.objects.filter(society=society).filter(deadline__gte=timezone.now()).order_by('deadline')
    
    context = {'society':society, 'shows':shows, 'auditions':auditions, 'techieads':techieads, 'showapps':showapps, 'societyapps':societyapps, 'current_pagetype':'societies'}
    return render(request, 'drama/society.html', context)

def venue(request,slug):
    venue = get_object_or_404(Venue,slug=slug)
    shows = Show.objects.filter(performance__venue=venue).distinct()
    auditions = AuditionInstance.objects.filter(audition__show__performance__venue=venue).filter(end_datetime__gte=timezone.now()).order_by('end_datetime','start_time').distinct()
    techieads = TechieAd.objects.filter(show__performance__venue=venue).filter(deadline__gte=timezone.now()).order_by('deadline').distinct()
    showapps = ShowApplication.objects.filter(show__performance__venue=venue).filter(deadline__gte=timezone.now()).order_by('deadline')
    venueapps = VenueApplication.objects.filter(venue=venue).filter(deadline__gte=timezone.now()).order_by('deadline')
    context = {'venue':venue, 'shows':shows, 'auditions':auditions, 'techieads':techieads, 'showapps':showapps, 'venueapps':venueapps, 'current_pagetype':'venues'}
    return render(request, 'drama/venue.html', context)

def role(request,slug):
    return HttpResponse("Hello World")

def auditions(request):
    aud_instances = AuditionInstance.objects.filter(end_datetime__gte=timezone.now()).order_by('end_datetime','start_time').select_related('audition')
    seen = set()
    seen_add = seen.add
    ads = [i.audition for i in aud_instances if i.audition.id not in seen and not seen_add(i.audition.id)]
    context = {'ads': ads, 'current_roletype':'auditions', 'current_pagetype':'vacancies'}
    return render(request, 'drama/auditions.html', context)

def auditions_diary(request):
    return HttpResponse("Hello World")

def auditions_item(request,slug):
    return redirect(reverse('auditions') + '#' + slug)

def applications(request):
    showads = ShowApplication.objects.filter(deadline__gte=timezone.now()).order_by('deadline')
    socads = SocietyApplication.objects.filter(deadline__gte=timezone.now()).order_by('deadline')
    venueads = VenueApplication.objects.filter(deadline__gte=timezone.now()).order_by('deadline')
    context = {'showads': showads, 'venueads': venueads, 'socads':socads, 'current_roletype':'applications', 'current_pagetype':'vacancies'}
    return render(request, 'drama/applications.html', context)

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

def autocomplete(request):
    sqs = SearchQuerySet().autocomplete(auto=request.GET.get('q','')).load_all()[:10]
    suggestions = [{'name':result.object.name,
                   'string':result.object.dec_string,
                   'link':reverse(result.object.get_cname(), kwargs={'slug':result.object.slug}),
                   'type':result.object.get_cname(),
                   } for result in sqs]
    data = json.dumps(suggestions)
    return HttpResponse(data, content_type='application/json')

def about(request):
    return HttpResponse("Hello World")

def development(request):
    return HttpResponse("Hello World")

def contact_us(request):
    return HttpResponse("Hello World")

def privacy(request):
    return HttpResponse("Hello World")

def my_redirect(request, model_name, slug, *args, **kwargs):
    return redirect(reverse(model_name) + '#' + slug)

def display(request, *args, **kwargs):
    return HttpResponse("Hello World")

def new(request, *args, **kwargs):
    return HttpResponse("Hello World")

def edit(request, *args, **kwargs):
    return HttpResponse("Hello World")

def remove(request, *args, **kwargs):
    return HttpResponse("Hello World")

