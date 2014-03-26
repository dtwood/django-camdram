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

def applications(request):
    showads = ShowApplication.objects.filter(deadline__gte=timezone.now()).order_by('deadline')
    socads = SocietyApplication.objects.filter(deadline__gte=timezone.now()).order_by('deadline')
    venueads = VenueApplication.objects.filter(deadline__gte=timezone.now()).order_by('deadline')
    context = {'showads': showads, 'venueads': venueads, 'socads':socads, 'current_roletype':'applications', 'current_pagetype':'vacancies'}
    return render(request, 'drama/applications.html', context)

def ad_role(request, show_slug, role_slug):
    role = get_object_or_404(TechieAdRole,slug=role_slug,ad__show__slug=show_slug)
    context = {'role':role, 'current_roletype':'', 'current_pagetype':'vacancies'}
    return render(request, 'drama/ad_role.html', context)

def techieads(request):
    ads = TechieAd.objects.filter(deadline__gte=timezone.now()).order_by('deadline')
    context = {'ads': ads, 'current_roletype':'techie', 'current_pagetype':'vacancies'}
    return render(request, 'drama/techiead.html', context)

def autocomplete(request):
    sqs = SearchQuerySet().autocomplete(auto=request.GET.get('q','')).load_all()[:10]
    suggestions = [{'name':result.object.name,
                   'string':result.object.dec_string,
                   'link':reverse('display', kwargs={'model_name':result.object.get_cname(), 'slug':result.object.slug}),
                   'type':result.object.get_cname(),
                   } for result in sqs]
    data = json.dumps(suggestions)
    return HttpResponse(data, content_type='application/json')

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

class FormSetMixin():
    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance with the passed
        POST variables and then checked for validity.
        """
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if self.object:
            form.bind_formsets(self.request.POST, self.request.FILES, instance=self.object)
        else:
            form.bind_formsets(self.request.POST, self.request.FILES)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
        
    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates a blank version of the form.
        """
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if self.object:
            form.bind_formsets(instance=self.object)
        else:
            form.bind_formsets()
        return self.render_to_response(self.get_context_data(form=form))
    
    def get_context_data(self, *args, **kwargs):
        context = super(FormSetMixin, self).get_context_data(**kwargs)
        form = context['form']
        formsets = form.get_context()
        for k,v in formsets.items():
            context[k] = v
        return context
    
class MyCreateView(FormSetMixin, CreateView):
    def get(self, request, *args, **kwargs):
        self.object = None
        return super(MyCreateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = None
        return super(MyCreateView, self).post(request, *args, **kwargs)
        
    def get_context_data(self, **kwargs):
        context = super(MyCreateView, self).get_context_data(**kwargs)
        context['content_form'] = context['form']
        del context['form']
        return context
        
class MyUpdateView(FormSetMixin, UpdateView):
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(MyUpdateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(MyUpdateView, self).post(request, *args, **kwargs)
        
    def get_context_data(self, **kwargs):
        context = super(MyUpdateView, self).get_context_data(**kwargs)
        context['content_form'] = context['form']
        del context['form']
        return context
    
class MyDeleteView(DeleteView):
    def get_context_data(self, **kwargs):
        context = super(MyDeleteView, self).get_context_data(**kwargs)
        context['content_form'] = context['form']
        del context['form']
        return context

class MyListView(ListView):
    model_name=None
    def get_context_data(self, **kwargs):
        context = super(MyListView, self).get_context_data(**kwargs)
        context['current_pagetype'] = self.model_name
        return context
    
def display(request, model, template=None, get_context=None, *args, **kwargs):
    if not get_context:
        def get_context(self, **kwargs):
            return super(DetailView, self).get_context_data(**kwargs)
    view = MyDetailView.as_view(model=model,get_context=get_context, template_name=template)
    return view(request, *args, **kwargs)

def new(request, model, form=None, *args, **kwargs):
    view = MyCreateView.as_view(model=model,form_class=form)
    return view(request, *args, **kwargs)
    
def edit(request, model, form=None, *args, **kwargs):
    view = MyUpdateView.as_view(model=model, form_class=form)
    return view(request, *args, **kwargs)
    
def remove(request, model, *args, **kwargs):
    view = MyDeleteView.as_view(model=model)
    return view(request, *args, **kwargs)

def list(request, model, model_name, *args, **kwargs):
    view = MyListView.as_view(model=model, model_name=model_name)
    return view(request, model_name=model_name, *args, **kwargs)
