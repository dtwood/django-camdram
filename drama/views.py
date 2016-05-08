from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.http import HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from haystack.query import SearchQuerySet
from django.views.generic import TemplateView, DetailView, CreateView, UpdateView, DeleteView, ListView, View
from drama import util, models, forms
import json
import datetime
import dal
import hashlib
from registration.backends.default.views import RegistrationView
from guardian.shortcuts import assign_perm, get_objects_for_user, remove_perm, get_users_with_perms
from collections import namedtuple
from django.views.decorators.http import require_http_methods, require_POST
import reversion
from django.db import transaction
from django.template import defaultfilters

WeekContainer = namedtuple('WeekContainer', 'name label diary start_date current')

def index(request):
    today = timezone.now().date()
    start_date = datetime.date.fromordinal(today.toordinal() - today.weekday())
    end_date = datetime.date.fromordinal(today.toordinal() - today.weekday() + 6)
    performance_objects = models.Performance.objects.filter(end_date__gte=start_date, start_date__lte=end_date, show__approved=True).distinct()
    performances = 0
    for p in performance_objects:
        performances += p.performance_count(start_date, end_date)
    dates = [start_date + datetime.timedelta(weeks=x) for x in range(-4,11)]
    weeks = []
    for date in dates:
        current = False
        if date == start_date:
            current = True
            label = 'This week'
        elif date == start_date + datetime.timedelta(weeks=1):
            label = 'Next week'
        else:
            label = '{} - {}'.format(defaultfilters.date(date,'j b').title(), defaultfilters.date(date + datetime.timedelta(days=6),'j b').title())
        weeks.append(WeekContainer(name=models.TermDate.get_weeklabel(date),
                                   current = current,
                                   label=label,
                                   diary=util.diary_week(models.Performance.objects.approved(), date, hide=(not current)),
                                   start_date = date))
    context = {
        'shows': models.Show.objects.filter(performance__end_date__gte=start_date, performance__start_date__lte=end_date).filter(approved=True).distinct().count(),
        'venues': models.Venue.objects.filter(performance__end_date__gte=start_date, performance__start_date__lte=end_date).filter(performance__show__approved=True).distinct().count(),
        'people': models.Person.objects.filter(roleinstance__show__performance__end_date__gte=start_date, roleinstance__show__performance__start_date__lte=end_date, roleinstance__show__approved=True).distinct().count(),
        'performances': performances,
        'auditions': models.AuditionInstance.objects.filter(end_datetime__gte=timezone.now()).order_by('end_datetime', 'start_time').filter(audition__show__approved=True).select_related('audition')[0:3],
        'techieads': models.TechieAd.objects.filter(deadline__gte=timezone.now()).filter(show__approved=True).order_by('deadline')[0:3],
        'societyapps': models.SocietyApplication.objects.filter(deadline__gte=timezone.now()).filter(society__approved=True).order_by('deadline')[0:2],
        'venueapps': models.VenueApplication.objects.filter(deadline__gte=timezone.now()).filter(venue__approved=True).order_by('deadline')[0:2],
        'showapps': models.ShowApplication.objects.filter(deadline__gte=timezone.now()).filter(show__approved=True).order_by('deadline')[0:3],
        'diary': util.diary_week(models.Performance.objects.filter(show__approved=True), today),
        'last_year': models.Show.objects.filter(end_date__gte=datetime.date(start_date.year - 1, start_date.month, start_date.day), start_date__lte=datetime.date(end_date.year - 1, end_date.month, end_date.day)).approved()[0:5],
        '2_years': models.Show.objects.filter(end_date__gte=datetime.date(start_date.year - 2, start_date.month, start_date.day), start_date__lte=datetime.date(end_date.year - 2, end_date.month, end_date.day)).approved()[0:5],
        '5_years': models.Show.objects.filter(end_date__gte=datetime.date(start_date.year - 5, start_date.month, start_date.day), start_date__lte=datetime.date(end_date.year - 5, end_date.month, end_date.day)).approved()[0:5],
        'weeks': weeks,
        'news': models.SocialPost.objects.all()[0:15],
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
    events = models.Performance.objects.filter(show__approved=True)
    diary = util.diary(week, end, events, with_labels=True)
    current_term = models.TermDate.get_term(timezone.now())
    jump_form = forms.DiaryJumpForm(initial={'term':current_term.term, 'year':current_term.year})
    return render(request, "drama/diary.html", {'diary': diary, 'start':week, 'end':end, 'prev':prev, 'jump_form': jump_form})

def diary_week(request):
    if 'week' in request.GET:
        week = datetime.datetime.strptime(request.GET['week'],"%Y-%m-%d").date()
    else:
        raise Http404
    events = models.Performance.objects.filter(show__approved=True)
    term_label, week_label = models.TermDate.get_label(week)
    diary_week = {'html':util.diary_week(events, week, label=week_label), 'term_label':term_label}
    data = json.dumps(diary_week)
    return HttpResponse(data, content_type='application/json')

def diary_jump(request):
    form = forms.DiaryJumpForm(request.GET)
    if form.is_valid():
        term = get_object_or_404(models.TermDate,term=form.cleaned_data['term'], year=form.cleaned_data['year'])
        return redirect(reverse('diary', kwargs={'week': term.start.strftime('%Y-%m-%d')}))
    else:
        raise Http404

def auditions(request):
    aud_instances = models.AuditionInstance.objects.filter(end_datetime__gte=timezone.now()).order_by(
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
    showads = models.ShowApplication.objects.filter(
        deadline__gte=timezone.now()).filter(show__approved=True).order_by('deadline')
    socads = models.SocietyApplication.objects.filter(
        deadline__gte=timezone.now()).filter(society__approved=True).order_by('deadline')
    venueads = models.VenueApplication.objects.filter(
        deadline__gte=timezone.now()).filter(venue__approved=True).order_by('deadline')
    context = {'showads': showads, 'venueads': venueads, 'socads': socads,
               'current_roletype': 'applications', 'current_pagetype': 'vacancies'}
    return render(request, 'drama/applications.html', context)


def ad_role(request, show_slug, role_slug):
    role = get_object_or_404(
        models.TechieAdRole, slug=role_slug, ad__show__slug=show_slug)
    context = {'role': role, 'current_roletype': '',
               'current_pagetype': 'vacancies'}
    return render(request, 'drama/ad_role.html', context)


def techieads(request):
    ads = models.TechieAd.objects.filter(
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


def techiead_item(request, slug, *args, **kwargs):
    return redirect(reverse('technical') + '#' + slug)

def audition_item(request, slug, *args, **kwargs):
    return redirect(reverse('auditions') + '#' + slug)

def application_item(request, slug, *args, **kwargs):
    return redirect(reverse('applications') + '#' + slug)


class MyCreateView(CreateView):
    model_name = None

    def get_context_data(self, **kwargs):
        context = super(MyCreateView, self).get_context_data(**kwargs)
        context['content_form'] = context['form']
        context['current_pagetype'] = self.model_name
        del context['form']
        return context

    @transaction.atomic()
    def form_valid(self, form):
        if self.model_name in ('shows',):
            self.success_url = '/'
            super(MyCreateView, self).form_valid(form)
            self.object.reslug()
            self.success_url = False
            result = redirect(self.get_success_url())
        else:
            result = super(MyCreateView, self).form_valid(form)
        log_item = models.LogItem(cat='CREATE', datetime=timezone.now(), user=self.request.user, content_object=self.object, desc='')
        log_item.save()
        if self.request.user.has_perm('drama.approve_' + self.object.class_name(), self.object):
            self.object.approve()
            log_item = models.LogItem(cat='APPROVE', datetime=timezone.now(), user=self.request.user, content_object=self.object, desc='Auto-approved')
            log_item.save()
        else:
            item = ApprovalQueueItem(created_by=self.request.user, content_object=self.object)
            item.save()
        self.object.grant_admin(self.request.user)
        return result

class MyDeleteView(DeleteView):
    on_success=None
    
    def __init__(self, *args, on_success=None, **kwargs):
        self.on_success=on_success
        return super(MyDeleteView, self).__init__(*args, **kwargs)
    
    @transaction.atomic()
    def delete(self, request, *args, **kwargs):
        if self.on_success:
            fun = self.on_success
            fun()
        return super(MyDeleteView, self).delete(self, request, *args, **kwargs)


class EmailRegistrationView(RegistrationView):
    form_class = forms.EmailRegistrationForm
    def register(self, request, **cleaned_data):
        cleaned_data['username'] = hashlib.md5(cleaned_data['email'].encode('utf-8')).hexdigest()[0:30]
        return super(EmailRegistrationView, self).register(request, **cleaned_data)
    
@login_required
def show_admin(request):
    shows = get_objects_for_user(request.user, 'drama.change_show')
    return render(request, 'drama/show_admin.html', {'shows':shows})

@login_required
def approval_queue(request):
    queue = [x for x in models.ApprovalQueueItem.objects.all() if request.user.has_perm('drama.approve_' + x.content_object.class_name(), x.content_object)]
    return render(request, 'drama/approval_queue.html', {'queue':queue})
    
@login_required
@require_POST
@transaction.atomic()
def approval_ignore(request, key=None):
    item = get_object_or_404(models.ApprovalQueueItem,pk=key)
    if request.user.has_perm('drama.approve_' + item.content_object.class_name(), item.content_object):
        item.delete()
        log_item = models.LogItem(cat='APPROVE', datetime=timezone.now(), user=request.user, content_object=item.object, desc='Ignored')
        log_item.save()
        return redirect(reverse('approvals'))
    else:
        raise PermissionDenied

@login_required
@require_POST
@transaction.atomic()
def approval_approve(request, key=None):
    item = get_object_or_404(models.ApprovalQueueItem,pk=key)
    if request.user.has_perm('drama.approve_' + item.content_object.class_name(), item.content_object):
        item.content_object.approve()
        log_item = models.LogItem(cat='APPROVE', datetime=timezone.now(), user=request.user, content_object=item.object, desc='Approved')
        log_item.save()
        return redirect(reverse('approvals'))
    else:
        raise PermissionDenied
    
