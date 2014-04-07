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
import json
import autocomplete_light
import hashlib
from registration.backends.simple.views import RegistrationView
from guardian.shortcuts import assign_perm, get_objects_for_user, remove_perm, get_users_with_perms


def index(request):
    return render(request, 'drama/base.html')


def diary(request):
    return HttpResponse("Hello World")


def auditions(request):
    aud_instances = AuditionInstance.objects.filter(end_datetime__gte=timezone.now()).order_by(
        'end_datetime', 'start_time').select_related('audition')
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
        deadline__gte=timezone.now()).order_by('deadline')
    socads = SocietyApplication.objects.filter(
        deadline__gte=timezone.now()).order_by('deadline')
    venueads = VenueApplication.objects.filter(
        deadline__gte=timezone.now()).order_by('deadline')
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
        deadline__gte=timezone.now()).order_by('deadline')
    context = {'ads': ads, 'current_roletype': 'techie',
               'current_pagetype': 'vacancies'}
    return render(request, 'drama/techiead.html', context)


def autocomplete(request):
    sqs = SearchQuerySet().autocomplete(
        auto=request.GET.get('q', '')).load_all()[:10]
    suggestions = [{'name': result.object.name,
                   'string': result.object.dec_string,
                   'link': reverse('display', kwargs={'model_name': result.object.get_cname(), 'slug': result.object.slug}),
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
    get_context = None
    user = None

    def get_context_data(self, **kwargs):
        func = self.get_context
        return func(self, user=self.user, **kwargs)


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


def display(request, model, template=None, get_context=None, *args, **kwargs):
    if not get_context:
        def get_context(self, **kwargs):
            return super(DetailView, self).get_context_data(**kwargs)
    view = MyDetailView.as_view(
        model=model, get_context=get_context, template_name=template, user=request.user)
    return view(request, *args, **kwargs)

@login_required
def new(request, model, model_name=None, form=None, *args, **kwargs):
    if request.user.has_perm('drama.add_' + model.__name__.lower()):
        view = MyCreateView.as_view(model=model, model_name=model_name, form_class=form)
        return view(request, *args, **kwargs)
    else:
        raise PermissionDenied


@login_required
def edit(request, model, slug, model_name=None, form=None, *args, **kwargs):
    item = get_object_or_404(model, slug=slug)
    if request.user.has_perm('drama.change_' + model.__name__.lower(), item):
        view = MyUpdateView.as_view(model=model, model_name=model_name, form_class=form)
        return view(request, slug=slug, *args, **kwargs)
    else:
        raise PermissionDenied


@login_required
def remove(request, model, slug, *args, **kwargs):
    item = get_object_or_404(model, slug=slug)
    if request.user.has_perm('drama.delete_' + model.__name__.lower(), item):
        view = DeleteView.as_view(model=model, success_url="/")
        return view(request, slug=slug, *args, **kwargs)
    else:
        raise PermissionDenied


def list(request, model, model_name, *args, **kwargs):
    view = MyListView.as_view(model=model, model_name=model_name)
    return view(request, model_name=model_name, *args, **kwargs)


@login_required
def related_edit(request, model, form, slug, *args, **kwargs):
    show = get_object_or_404(Show, slug=slug)
    if request.user.has_perm('drama.change_' + show.__class__.__name__.lower(), show):
        try:
            item = model.objects.filter(show__slug=slug)[0]
            view = ItemUpdateView.as_view(model=model, form_class=form, object=item, success_url=reverse('display', kwargs={'model_name':'shows', 'slug':slug}), form_kwargs={'parent':show, 'parent_name':'show'}, parent=show)
        except IndexError:
            view = MyCreateView.as_view(model=model, form_class=form, form_kwargs={'parent':show, 'parent_name':'show'}, success_url=reverse('display', kwargs={'model_name':'shows', 'slug':slug}), parent=show)
        return view(request, *args, **kwargs)
    else:
        raise PermissionDenied

@login_required
def related_remove(request, model, slug, *args, **kwargs):
    show = get_object_or_404(Show, slug=slug)
    if request.user.has_perm('drama.change_' + show.__class__.__name__.lower(), show):
        try:
            item = model.objects.filter(show__slug=slug)[0]
        except IndexError:
            raise Http404
        view = DeleteView.as_view(model=model, success_url="/")
        return view(request, pk=item.pk, *args, **kwargs)
    else:
        raise PermissionDenied
    
    
@login_required
@csrf_protect
def application_edit(request, model, slug, form, prefix, *args, **kwargs):
    parent = get_object_or_404(model, slug=slug)
    if request.user.has_perm('drama.change_' + model.__name__.lower(), parent):
        if request.method == 'GET':
            context = {}
            context['content_form'] = form(instance=parent)
            context['parent'] = parent
            context['prefix'] = prefix
            return render(request, 'drama/application_formset.html', context)
        elif request.method == 'POST':
            bound_form = form(request.POST, instance=parent)
            if bound_form.is_valid():
                bound_form.save()
                return redirect(parent.get_absolute_url())
            else:
                context = {}
                context['content_form'] = bound_form
                context['parent'] = parent
                context['prefix'] = prefix
                return render(request, 'drama/application_formset.html', context)
        else:
            raise Http404
    else:
        raise PermissionDenied

@login_required
@csrf_protect
def remove_role(request, slug, id, *args, **kwargs):
    show = get_object_or_404(Show, slug=slug)
    role = get_object_or_404(RoleInstance, id=id)
    if role.show != show:
        raise Http404
    if request.user.has_perm('drama.change_show', show):
        role.delete()
        return redirect(show.get_absolute_url())
    else:
        raise PermissionDenied

@login_required
@csrf_protect
def add_cast(request, slug, *args, **kwargs):
    show = get_object_or_404(Show, slug=slug)
    if request.method == "POST":
        if request.user.has_perm('drama.change_show', show):
            form = CastForm(request.POST)
            if form.is_valid():
                character = get_object_or_404(Role,name='Character')
                name = form.cleaned_data['role']
                person = form.cleaned_data['person']
                r = RoleInstance(name=name, show=show,person=person,role=character)
                r.save()
            return redirect(show.get_absolute_url())
        else:
            raise PermissionDenied
    else:
        return redirect(show.get_absolute_url())


@login_required
@csrf_protect
def add_band(request, slug, *args, **kwargs):
    show = get_object_or_404(Show, slug=slug)
    if request.method == "POST":
        if request.user.has_perm('drama.change_show', show):
            form = BandForm(request.POST)
            if form.is_valid():
                role = form.cleaned_data['role']
                name = form.cleaned_data['name']
                person = form.cleaned_data['person']
                r = RoleInstance(name=name, show=show,person=person,role=role)
                r.save()
            return redirect(show.get_absolute_url())
        else:
            raise PermissionDenied
    else:
        return redirect(show.get_absolute_url())


@login_required
@csrf_protect
def add_prod(request, slug, *args, **kwargs):
    show = get_object_or_404(Show, slug=slug)
    if request.method == "POST":
        if request.user.has_perm('drama.change_show', show):
            form = ProdForm(request.POST)
            if form.is_valid():
                role = form.cleaned_data['role']
                name = form.cleaned_data['name']
                person = form.cleaned_data['person']
                r = RoleInstance(name=name, show=show,person=person,role=role)
                r.save()
            return redirect(show.get_absolute_url())
        else:
            raise PermissionDenied
    else:
        return redirect(show.get_absolute_url())
    
@login_required
def role_reorder(request, slug, *args, **kwargs):
    show = get_object_or_404(Show, slug=slug)
    if request.method == "POST":
        if request.user.has_perm('drama.change_show', show):
            for index, item_id in enumerate(request.POST.getlist('role[]')):
                item = get_object_or_404(RoleInstance, id=int(str(item_id)))
                if not item.show == show:
                    raise PermissionDenied
                item.sort = index
                item.save()
            return HttpResponse('')
        else:
            raise PermissionDenied
    else:
        return HttpResponse('')

@login_required
def show_admin(request):
    shows = get_objects_for_user(request.user, 'drama.change_show')
    return render(request, 'drama/show_admin.html', {'shows':shows})

@login_required
def link_user(request, slug, *args, **kwargs):
    person = get_object_or_404(Person, slug=slug)
    user = request.user
    if person.user is not None:
        raise PermissionDenied
    else:
        try:
            user.person
        except Person.DoesNotExist:
            pass
        else:
            #May want to think about making this stricter
           remove_perm('change_person', user, person)
        person.user = user
        person.save()
        assign_perm('change_person', user, person)
        user.first_name = person.name
        user.save()
        return redirect(person.get_absolute_url())

@login_required
def change_admins(request, slug, *args, **kwargs):
    show = get_object_or_404(Show, slug=slug)
    if request.user.has_perm('change_show', show):
        if request.method == "GET":
            context = {
                'users': get_users_with_perms(show, with_group_users=False),
                'pending_users': show.pendingadmin_set.all(),
                'new_admin_form': AdminForm(),
                'parent': show,
                'model_name': 'shows',
            }
            return render(request, 'drama/change_admins.html', context)
        elif request.method == "POST":
            form = AdminForm(request.POST)
            if form.is_valid():
                show.add_admin(form.cleaned_data['email'])
                return redirect(show.get_absolute_url())
            else:
                context = {
                    'users': get_users_with_perms(show, with_group_users=False),
                    'pending_users': show.pendingadmin_set.all(),
                    'new_admin_form': form,
                    'parent': show,
                    'model_name': 'shows',
                }
                return render(request, 'drama/change_admins.html', context)
        else:
            return redirect(show.get_absolute_url())
    else:
        raise PermissionDenied

@login_required
def change_admin_group(request, slug, model, model_name, *args, **kwargs):
    item = get_object_or_404(model, slug=slug)
    if request.user.has_perm('change_' + model.__name__.lower(), item):
        if request.method == "GET":
            context = {
                'users': item.group.user_set.all(),
                'pending_users': item.group.pendinggroupmember_set.all(),
                'new_admin_form': AdminForm(),
                'parent': item,
                'model_name': model_name,
            }
            return render(request, 'drama/change_admins.html', context)
        elif request.method == "POST":
            form = AdminForm(request.POST)
            if form.is_valid():
                item.add_admin(form.cleaned_data['email'])
                return redirect(item.get_absolute_url())
            else:
                context = {
                    'users': item.group.user_set.all(),
                    'pending_users': item.group.pendinggroupmember_set.all(),
                    'new_admin_form': form,
                    'parent': item,
                    'model_name': model_name,
                }
                return render(request, 'drama/change_admins.html', context)
        else:
            return redirect(item.get_absolute_url())
    else:
        raise PermissionDenied

@login_required
def revoke_admin(request, model, slug, username, model_name, *args, **kwargs):
    item = get_object_or_404(model, slug=slug)
    if request.user.has_perm('change_' + model.__name__.lower(), item):
        item.remove_admin(username)
        return redirect(reverse('change_admins',kwargs={'model_name':model_name, 'slug':slug}))
    else:
        raise PermissionDenied

@login_required
def approve(request, model, slug, *args, **kwargs):
    item = get_object_or_404(model, slug=slug)
    if request.user.has_perm('approve_' + model.__name__.lower(), item):
        item.approve()
        return redirect(item.get_absolute_url())
    else:
        raise PermissionDenied

@login_required
def unapprove(request, model, slug, *args, **kwargs):
    item = get_object_or_404(model, slug=slug)
    if request.user.has_perm('approve_' + model.__name__.lower(), item):
        item.unapprove()
        return redirect(item.get_absolute_url())
    else:
        raise PermissionDenied

