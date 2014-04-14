from django.shortcuts import render, get_object_or_404, redirect
from drama.models import *
from drama.forms import *
from django.utils import timezone
from django.http import HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from haystack.query import SearchQuerySet
from django.views.generic import TemplateView, DetailView, CreateView, UpdateView, DeleteView, ListView, View
from drama import util
import json
import datetime
import autocomplete_light
import hashlib
from registration.backends.simple.views import RegistrationView
from guardian.shortcuts import assign_perm, get_objects_for_user, remove_perm, get_users_with_perms


def index(request):
    return render(request, 'drama/index.html', {'events': Performance.objects.all()})


def diary(request, week=None):
    if week is None:
        week = timezone.now().date()
    else:
        week = datetime.datetime.strptime(week,"%Y-%m-%d").date()
    if 'end' in request.GET:
        end = datetime.datetime.strptime(request.GET['end'],"%Y-%m-%d").date()
    else:
        end = week + datetime.timedelta(days=56)
    prev = week - datetime.timedelta(days=7)
    events = Performance.objects.filter(show__approved=True)
    diary = util.diary(week, end, events, with_labels=True)
    return render(request, "drama/diary.html", {'diary': diary, 'start':week, 'end':end, 'prev':prev})

def diary_week(request):
    if 'week' in request.GET:
        week = datetime.datetime.strptime(request.GET['week'],"%Y-%m-%d").date()
    else:
        raise Http404
    events = Performance.objects.filter(show__approved=True)
    term_label, week_label = TermDate.get_label(week)
    diary_week = {'html':util.diary_week(events, week, label=week_label), 'term_label':term_label}
    data = json.dumps(diary_week)
    return HttpResponse(data, content_type='application/json')

def auditions(request):
    aud_instances = AuditionInstance.objects.filter(end_datetime__gte=timezone.now()).order_by(
        'end_datetime', 'start_time').filter(audition__show__approved=True).select_related('audition')
    seen = set()
    seen_add = seen.add
    ads = [i.audition for i in aud_instances if i.audition.id not in seen and not seen_add(
        i.audition.id)]
    context = {'ads': ads, 'current_roletype': 'auditions',
               'current_pagetype': 'vacancies'}
    return render(request, 'drama/auditions.html', context)


def auditions_diary(request):
    return HttpResponse("Hello World")


def applications(request):
    showads = ShowApplication.objects.filter(
        deadline__gte=timezone.now()).filter(show__approved=True).order_by('deadline')
    socads = SocietyApplication.objects.filter(
        deadline__gte=timezone.now()).filter(society__approved=True).order_by('deadline')
    venueads = VenueApplication.objects.filter(
        deadline__gte=timezone.now()).filter(venue__approved=True).order_by('deadline')
    context = {'showads': showads, 'venueads': venueads, 'socads': socads,
               'current_roletype': 'applications', 'current_pagetype': 'vacancies'}
    return render(request, 'drama/applications.html', context)


def ad_role(request, show_slug, role_slug):
    role = get_object_or_404(
        TechieAdRole, slug=role_slug, ad__show__slug=show_slug)
    context = {'role': role, 'current_roletype': '',
               'current_pagetype': 'vacancies'}
    return render(request, 'drama/ad_role.html', context)


def techieads(request):
    ads = TechieAd.objects.filter(
        deadline__gte=timezone.now()).filter(show__approved=True).order_by('deadline')
    context = {'ads': ads, 'current_roletype': 'techie',
               'current_pagetype': 'vacancies'}
    return render(request, 'drama/techiead.html', context)


def autocomplete(request):
    sqs = SearchQuerySet().autocomplete(
        auto=request.GET.get('q', '')).load_all()[:10]
    suggestions = [{'name': result.object.name,
                   'string': result.object.dec_string,
                   'link': result.object.get_absolute_url(),
                   'type': result.object.get_cname(),
                    } for result in sqs]
    data = json.dumps(suggestions)
    return HttpResponse(data, content_type='application/json')


def development(request):
    return HttpResponse("Hello World")


def contact_us(request):
    return HttpResponse("Hello World")


def my_redirect(request, model_name, slug, *args, **kwargs):
    return redirect(reverse(model_name) + '#' + slug)


class MyDetailView(DetailView):
    user = None

    def get_context_data(self, **kwargs):
        request = self.request
        context = super(MyDetailView, self).get_context_data(**kwargs)
        context.update(self.object.get_detail_context(request))
        return context


class FormSetMixin:
    form_kwargs={}

    def get_form_kwargs(self):
        kwargs = super(FormSetMixin, self).get_form_kwargs()
        kwargs.update(self.form_kwargs)
        return kwargs

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance with the passed
        POST variables and then checked for validity.
        """
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if self.object:
            form.bind_formsets(
                self.request.POST, self.request.FILES, instance=self.object)
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
        for k, v in formsets.items():
            context[k] = v
        return context


class MyCreateView(FormSetMixin, autocomplete_light.CreateView):
    parent = None
    model_name = None

    def get(self, request, *args, **kwargs):
        self.object = None
        return super(MyCreateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = None
        return super(MyCreateView, self).post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(MyCreateView, self).get_context_data(**kwargs)
        context['content_form'] = context['form']
        context['parent'] = self.parent
        context['current_pagetype'] = self.model_name
        del context['form']
        return context

    def form_valid(self, form):
        result = super(MyCreateView, self).form_valid(form)
        if self.model_name in ('shows',):
            assign_perm('drama.change_' + self.object.__class__.__name__.lower(), self.request.user, self.object)
        return result

    def get_success_url(self):
        if self.success_url:
            return self.success_url
        else:
            return super(MyCreateView, self).get_success_url()


class MyUpdateView(FormSetMixin, UpdateView):
    model_name = None
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(MyUpdateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(MyUpdateView, self).post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(MyUpdateView, self).get_context_data(**kwargs)
        context['content_form'] = context['form']
        context['current_pagetype'] = self.model_name
        del context['form']
        return context


class MyListView(ListView):
    model_name = None

    def get_context_data(self, **kwargs):
        context = super(MyListView, self).get_context_data(**kwargs)
        context['current_pagetype'] = self.model_name
        return context

    def get_queryset(self, *args, **kwargs):
        return super(MyListView, self).get_queryset(*args, **kwargs).filter(approved=True)

class ItemUpdateView(FormSetMixin, UpdateView):
    object = None
    parent = None
    def get_context_data(self, **kwargs):
        context = super(ItemUpdateView, self).get_context_data(**kwargs)
        context['content_form'] = context['form']
        context['parent'] = self.parent
        del context['form']
        return context

    def get_success_url(self):
        if self.success_url:
            return self.success_url
        else:
            return super(MyCreateView, self).get_success_url()
    
class EmailRegistrationView(RegistrationView):
    form_class = EmailRegistrationForm
    def register(self, request, **cleaned_data):
        cleaned_data['username'] = hashlib.md5(cleaned_data['email'].encode('utf-8')).hexdigest()[0:30]
        return super(EmailRegistrationView, self).register(request, **cleaned_data)
    
@login_required
def show_admin(request):
    shows = get_objects_for_user(request.user, 'drama.change_show')
    return render(request, 'drama/show_admin.html', {'shows':shows})
