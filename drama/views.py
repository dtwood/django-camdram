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
from registration.backends.default.views import RegistrationView
from guardian.shortcuts import assign_perm, get_objects_for_user, remove_perm, get_users_with_perms
from collections import namedtuple
from django.views.decorators.http import require_http_methods, require_POST

WeekContainer = namedtuple('WeekContainer', 'label start_date end_date')

def index(request):
    today = timezone.now().date()
    start_date = datetime.date.fromordinal(today.toordinal() - today.weekday())
    end_date = datetime.date.fromordinal(today.toordinal() - today.weekday() + 6)
    performance_objects = Performance.objects.filter(end_date__gte=start_date, start_date__lte=end_date, show__approved=True).distinct()
    performances = 0
    for p in performance_objects:
        performances += p.performance_count(start_date, end_date)
    context = {
        'shows': Show.objects.filter(performance__end_date__gte=start_date, performance__start_date__lte=end_date).filter(approved=True).distinct().count(),
        'venues': Venue.objects.filter(performance__end_date__gte=start_date, performance__start_date__lte=end_date).filter(performance__show__approved=True).distinct().count(),
        'people': Person.objects.filter(roleinstance__show__performance__end_date__gte=start_date, roleinstance__show__performance__start_date__lte=end_date, roleinstance__show__approved=True).distinct().count(),
        'performances': performances,
        'auditions': AuditionInstance.objects.filter(end_datetime__gte=timezone.now()).order_by('end_datetime', 'start_time').filter(audition__show__approved=True).select_related('audition'),
        'techieads': TechieAd.objects.filter(deadline__gte=timezone.now()).filter(show__approved=True).order_by('deadline'),
        'societyapps': SocietyApplication.objects.filter(deadline__gte=timezone.now()).filter(society__approved=True).order_by('deadline'),
        'venueapps': VenueApplication.objects.filter(deadline__gte=timezone.now()).filter(venue__approved=True).order_by('deadline'),
        'showapps': ShowApplication.objects.filter(deadline__gte=timezone.now()).filter(show__approved=True).order_by('deadline'),
        'diary': util.diary_week(Performance.objects.filter(show__approved=True), today),
    }
    return render(request, 'drama/index.html', context)


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
    current_term = TermDate.get_term(timezone.now())
    jump_form = DiaryJumpForm(initial={'term':current_term.term, 'year':current_term.year})
    return render(request, "drama/diary.html", {'diary': diary, 'start':week, 'end':end, 'prev':prev, 'jump_form': jump_form})

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

def diary_jump(request):
    form = DiaryJumpForm(request.GET)
    if form.is_valid():
        term = get_object_or_404(TermDate,term=form.cleaned_data['term'], year=form.cleaned_data['year'])
        return redirect(reverse('diary', kwargs={'week': term.start.strftime('%Y-%m-%d')}))
    else:
        raise Http404

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
                   'type': result.object.class_name(),
                    } for result in sqs if result]
    data = json.dumps(suggestions)
    return HttpResponse(data, content_type='application/json')


def development(request):
    return HttpResponse("Hello World")


def contact_us(request):
    return HttpResponse("Hello World")


def my_redirect(request, model_name, slug, *args, **kwargs):
    return redirect(reverse(model_name) + '#' + slug)


class MyCreateView(autocomplete_light.CreateView):
    model_name = None

    def get_context_data(self, **kwargs):
        context = super(MyCreateView, self).get_context_data(**kwargs)
        context['content_form'] = context['form']
        context['current_pagetype'] = self.model_name
        del context['form']
        return context

    def form_valid(self, form):
        if self.model_name in ('shows',):
            self.success_url = '/'
            super(MyCreateView, self).form_valid(form)
            self.object.reslug()
            self.success_url = False
            result = redirect(self.get_success_url())
        else:
            result = super(MyCreateView, self).form_valid(form)
        if self.request.user.has_perm('drama.approve_' + self.object.class_name(), self.object):
            self.object.approve()
        else:
            item = ApprovalQueueItem(created_by=self.request.user, content_object=self.object)
            item.save()
        self.object.grant_admin(self.request.user)
        return result


class EmailRegistrationView(RegistrationView):
    form_class = EmailRegistrationForm
    def register(self, request, **cleaned_data):
        cleaned_data['username'] = hashlib.md5(cleaned_data['email'].encode('utf-8')).hexdigest()[0:30]
        return super(EmailRegistrationView, self).register(request, **cleaned_data)
    
@login_required
def show_admin(request):
    shows = get_objects_for_user(request.user, 'drama.change_show')
    return render(request, 'drama/show_admin.html', {'shows':shows})

@login_required
def approval_queue(request):
    queue = [x for x in ApprovalQueueItem.objects.all() if request.user.has_perm('drama.approve_' + x.content_object.class_name(), x.content_object)]
    return render(request, 'drama/approval_queue.html', {'queue':queue})
    
@login_required
@require_POST
def approval_ignore(request, key=None):
    item = get_object_or_404(ApprovalQueueItem,pk=key)
    if request.user.has_perm('drama.approve_' + item.content_object.class_name(), item.content_object):
        item.delete()
        return redirect(reverse('approvals'))
    else:
        raise PermissionDenied

@login_required
@require_POST
def approval_approve(request, key=None):
    item = get_object_or_404(ApprovalQueueItem,pk=key)
    if request.user.has_perm('drama.approve_' + item.content_object.class_name(), item.content_object):
        item.content_object.approve()
        return redirect(reverse('approvals'))
    else:
        raise PermissionDenied
    
