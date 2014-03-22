from django.shortcuts import render, get_object_or_404, redirect
from drama.models import *
from django.utils import timezone
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from haystack.query import SearchQuerySet
from django.views.generic import TemplateView, DetailView, CreateView, UpdateView, DeleteView, ListView
import json

def index(request):
    return HttpResponse("Hello World")

def diary(request):
    return HttpResponse("Hello World")

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
                   'link':reverse('display', kwargs={'model_name':result.object.get_cname(), 'slug':result.object.slug}),
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

class MyDetailView(DetailView):
    get_context = None
    def get_context_data(self, **kwargs):
        func = self.get_context
        return func(self, **kwargs)
    
def display(request, model, template=None, get_context=None, *args, **kwargs):
    if not get_context:
        def get_context(self, **kwargs):
            return super(DetailView, self).get_context_data(**kwargs)
    view = MyDetailView.as_view(model=model,get_context=get_context, template_name=template)
    return view(request, *args, **kwargs)

def new(request, model, form=None, *args, **kwargs):
    view = CreateView.as_view(model=model,form_class=form)
    return view(request, *args, **kwargs)
    
def edit(request, model, form=None, *args, **kwargs):
    view = UpdateView.as_view(model=model, form_class=form)
    return view(request, *args, **kwargs)
    
def remove(request, model, *args, **kwargs):
    view = DeleteView.as_view(model=model)
    return view(request, *args, **kwargs)

def list(request, model, *args, **kwargs):
    view = ListView.as_view(model=model)
    return view(request, *args, **kwargs)
