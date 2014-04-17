from collections import namedtuple
from django.views.generic import DeleteView
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, routers, permissions
from rest_framework.renderers import JSONRenderer, YAMLRenderer, BrowsableAPIRenderer, TemplateHTMLRenderer, StaticHTMLRenderer, XMLRenderer
from rest_framework.decorators import link, action, permission_classes, api_view
from rest_framework.response import Response
from rest_framework.permissions import DjangoModelPermissions, DjangoObjectPermissions, BasePermission
from drama import serializers, models, views, forms

Route = namedtuple('Route', ['url', 'mapping', 'name', 'initkwargs'])

class CamdramPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return request.user.has_perm('drama.add_' + view.model.class_name())
        
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return request.user.has_perm('drama.change_' + obj.class_name(),obj)
    

class ObjectViewSet(viewsets.ModelViewSet):
    lookup_field = 'slug'
    renderer_classes = (TemplateHTMLRenderer, BrowsableAPIRenderer, JSONRenderer, YAMLRenderer, XMLRenderer)
    permission_classes = (CamdramPermissions,)

    def new(self, request, *args, **kwargs):
        if request.user.has_perm('drama.create_' + self.model.class_name()):
            view = views.MyCreateView.as_view(model=self.model, model_name=self.model.get_cname(), form_class = self.form)
            return view(request, *args, **kwargs)
        else:
            raise PermissionDenied
    
    @action(methods=['GET', 'POST'])
    def edit(self, request, slug, *args, **kwargs):
        item = get_object_or_404(self.model, slug=slug)
        if request.user.has_perm('drama.change_' + self.model.class_name(), item):
            view = views.MyUpdateView.as_view(model=self.model, model_name=self.model.get_cname(), form_class = self.form)
            return view(request, slug=slug, *args, **kwargs)
        else:
            raise PermissionDenied

    @action(methods=['GET','POST'])
    def remove(self, request, slug, *args, **kwargs):
        item = get_object_or_404(self.model, slug=slug)
        if request.user.has_perm('drama.change_' + self.model.class_name(), item):
            view = DeleteView.as_view(model=self.model, success_url="/")
            return view(request, slug=slug, *args, **kwargs)
        else:
            raise PermissionDenied

    @link()
    def approve(self, request, slug, *args, **kwargs):
        item = get_object_or_404(self.model, slug=slug)
        if request.user.has_perm('drama.approve_' + item.class_name(), item):
            item.approve()
            return redirect(item.get_absolute_url())
        else:
            raise PermissionDenied

    @link()
    def unapprove(self, request, slug, *args, **kwargs):
        item = get_object_or_404(self.model, slug=slug)
        if request.user.has_perm('drama.approve_' + item.class_name(), item):
            item.unapprove()
            return redirect(item.get_absolute_url())
        else:
            raise PermissionDenied

    def list(self, request, *args, **kwargs):
        response = super(ObjectViewSet, self).list(request, *args, **kwargs)
        if request.accepted_renderer.format == 'html':
            response.template_name = "drama/" + self.model.__name__.lower() + "_list.html"
            response.data = {'object_list': self.object_list, 'current_pagetype': self.model.get_cname()}
        return response

    def retrieve(self, request, slug, *args, **kwargs):
        response = super(ObjectViewSet, self).retrieve(request, slug=slug, *args, **kwargs)
        if request.accepted_renderer.format == 'html':
            view = views.MyDetailView.as_view(model=self.model)
            return view(request, slug=slug, *args, **kwargs)
        return response


class OrganizationViewSet(ObjectViewSet):
    @action(methods=['GET', 'POST'])
    def applications(self, request, slug, *args, **kwargs):
        parent = get_object_or_404(self.model, slug=slug)
        if request.user.has_perm('drama.change_' + parent.class_name(), parent):
            if request.method == 'GET':
                context = {}
                context['content_form'] = self.applicationform(instance=parent)
                context['parent'] = parent
                context['prefix'] = parent.class_name()
                return render(request, 'drama/application_formset.html', context)
            elif request.method == 'POST':
                bound_form = self.applicationform(request.POST, instance=parent)
                if bound_form.is_valid():
                    bound_form.save()
                    return redirect(parent.get_absolute_url())
                else:
                    context = {}
                    context['content_form'] = bound_form
                    context['parent'] = parent
                    context['prefix'] = parent.class_name()
                    return render(request, 'drama/application_formset.html', context)
            else:
                raise Http404
        else:
            raise PermissionDenied


    @action(methods=['GET', 'POST'])
    def admins(self, request, slug, *args, **kwargs):
        item = get_object_or_404(self.model, slug=slug)
        if request.user.has_perm('change_' + item.class_name(), item):
            if request.method == "GET":
                context = {
                    'users': item.get_admins(),
                    'pending_users': item.get_pending_admins(),
                    'new_admin_form': forms.AdminForm(),
                    'parent': item,
                    'model_name': item.get_cname,
                }
                return render(request, 'drama/change_admins.html', context)
            elif request.method == "POST":
                form = forms.AdminForm(request.POST)
                if form.is_valid():
                    item.add_admin(form.cleaned_data['email'])
                    return redirect(item.get_absolute_url())
                else:
                    context = {
                        'users': item.get_admins(),
                        'pending_users': item.get_pending_admins(),
                        'new_admin_form': form,
                        'parent': item,
                        'model_name': item.get_cname(),
                    }
                    return render(request, 'drama/change_admins.html', context)
            elif request.method == "DELETE":
                username = request.DATA['username']
                item.remove_admin(username)
                return redirect(item.get_admins_url())
            else:
                return redirect(item.get_absolute_url())
        else:
            raise PermissionDenied

    @action(methods=['POST'])
    def revoke_admin(self, request, slug, *args, **kwargs):
        item = get_object_or_404(self.model, slug=slug)
        if request.user.has_perm('change_' + item.class_name(), item):
            username = request.DATA['username']
            item.remove_admin(username)
            return redirect(item.get_admins_url())
        else:
            raise PermissionDenied
        
class RoleViewSet(ObjectViewSet):
    queryset = models.Role.objects.all()
    serializer_class = serializers.RoleSerializer
    model = models.Role
    form = forms.RoleForm


class PersonViewSet(ObjectViewSet):
    queryset = models.Person.objects.all()
    serializer_class = serializers.PersonSerializer
    model = models.Person
    form = forms.PersonForm

    @link()
    def link(self, request, slug, *args, **kwargs):
        person = get_object_or_404(self.model, slug=slug)
        user = request.user
        if person.user is not None:
            raise PermissionDenied
        else:
            return person.link_user(user)

class SocietyViewSet(OrganizationViewSet):
    queryset = models.Society.objects.all()
    serializer_class = serializers.SocietySerializer
    model = models.Society
    form = forms.SocietyForm
    applicationform = forms.SocietyApplicationFormset


class VenueViewSet(OrganizationViewSet):
    queryset = models.Venue.objects.all()
    serializer_class = serializers.VenueSerializer
    model = models.Venue
    form = forms.VenueForm
    applicationform = forms.VenueApplicationFormset


class ShowViewSet(OrganizationViewSet):
    queryset = models.Show.objects.all()
    serializer_class = serializers.ShowSerializer
    model = models.Show
    form = forms.ShowForm
    applicationform = forms.ShowApplicationFormset

    @action(methods=['POST'])
    def add_cast(self, request, slug, *args, **kwargs):
        show = get_object_or_404(self.model, slug=slug)
        if request.method == "POST":
            if request.user.has_perm('drama.change_show', show):
                form = forms.CastForm(request.POST)
                if form.is_valid():
                    character = get_object_or_404(Role,name='Character')
                    name = form.cleaned_data['role']
                    person = form.cleaned_data['person']
                    r = models.RoleInstance(name=name, show=show,person=person,role=character)
                    r.save()
                return redirect(show.get_absolute_url())
            else:
                raise PermissionDenied
        else:
            return redirect(show.get_absolute_url())


    @action(methods=['POST'])
    def add_band(self, request, slug, *args, **kwargs):
        show = get_object_or_404(self.model, slug=slug)
        if request.method == "POST":
            if request.user.has_perm('drama.change_show', show):
                form = forms.BandForm(request.POST)
                if form.is_valid():
                    role = form.cleaned_data['role']
                    name = form.cleaned_data['name']
                    person = form.cleaned_data['person']
                    r = models.RoleInstance(name=name, show=show,person=person,role=role)
                    r.save()
                return redirect(show.get_absolute_url())
            else:
                raise PermissionDenied
        else:
            return redirect(show.get_absolute_url())


    @action(methods=['POST'])
    def add_prod(self, request, slug, *args, **kwargs):
        show = get_object_or_404(self.model, slug=slug)
        if request.method == "POST":
            if request.user.has_perm('drama.change_show', show):
                form = forms.ProdForm(request.POST)
                if form.is_valid():
                    role = form.cleaned_data['role']
                    name = form.cleaned_data['name']
                    person = form.cleaned_data['person']
                    r = models.RoleInstance(name=name, show=show,person=person,role=role)
                    r.save()
                return redirect(show.get_absolute_url())
            else:
                raise PermissionDenied
        else:
            return redirect(show.get_absolute_url())

    @action(methods=['POST'])
    def role_reorder(self, request, slug, *args, **kwargs):
        show = get_object_or_404(self.model, slug=slug)
        if request.user.has_perm('drama.change_show', show):
            for index, item_id in enumerate(request.POST.getlist('role[]')):
                item = get_object_or_404(models.RoleInstance, id=int(str(item_id)))
                if not item.show == show:
                    raise PermissionDenied
                item.sort = index
                item.save()
            return HttpResponse('')
        else:
            raise PermissionDenied

    @action(methods=['POST'])
    def remove_role(self, request, slug, *args, **kwargs):
        show = get_object_or_404(models.Show, slug=slug)
        role = get_object_or_404(models.RoleInstance, id=request.POST['role-id'])
        if role.show != show:
            raise Http404
        if request.user.has_perm('drama.change_show', show):
            role.delete()
            return redirect(show.get_absolute_url())
        else:
            raise PermissionDenied

    def related_edit(self, request, model, form, slug, *args, **kwargs):
        show = get_object_or_404(models.Show, slug=slug)
        if request.user.has_perm('drama.change_show', show):
            try:
                item = model.objects.filter(show__slug=slug)[0]
                view = views.ItemUpdateView.as_view(model=model, form_class=form, object=item, success_url=show.get_absolute_url(), form_kwargs={'parent':show, 'parent_name':'show'}, parent=show)
            except IndexError:
                view = views.MyCreateView.as_view(model=model, form_class=form, form_kwargs={'parent':show, 'parent_name':'show'}, success_url=show.get_absolute_url(), parent=show)
            return view(request, *args, **kwargs)
        else:
            raise PermissionDenied
    
    def related_remove(self, request, model, slug, *args, **kwargs):
        show = get_object_or_404(models.Show, slug=slug)
        if request.user.has_perm('drama.change_show', show):
            try:
                item = model.objects.filter(show__slug=slug)[0]
            except IndexError:
                raise Http404
            view = views.DeleteView.as_view(model=model, success_url="/")
            return view(request, pk=item.pk, *args, **kwargs)
        else:
            raise PermissionDenied

    @action(methods=['GET','POST'])
    def technical(self, request, slug):
        return self.related_edit(request, models.TechieAd, forms.TechieAdForm, slug) 

    @action(methods=['GET','POST'])
    def remove_technical(self, request, slug):
        return self.related_remove(request, models.TechieAd, slug) 

    @action(methods=['GET','POST'])
    def auditions(self, request, slug):
        return self.related_edit(request, models.Audition, forms.AuditionForm, slug) 

    @action(methods=['GET','POST'])
    def remove_auditions(self, request, slug):
        return self.related_remove(request, models.Audition, slug) 

class DramaRouter(routers.DefaultRouter):
    routes = [
        # List route.
        Route(
            url=r'^{prefix}{trailing_slash}$',
            mapping={
                'get': 'list',
                'post': 'create'
            },
            name='{basename}-list',
            initkwargs={'suffix': 'List'}
        ),
        # From-based create route
        Route(
            url=r'^{prefix}/new{trailing_slash}$',
            mapping={
                'get': 'new',
                'post': 'new',
                },
                name='{basename}-new',
                initkwargs={},
                ),
        # Detail route.
        Route(
            url=r'^{prefix}/{lookup}{trailing_slash}$',
            mapping={
                'get': 'retrieve',
                'put': 'update',
                'patch': 'partial_update',
                'delete': 'destroy'
            },
            name='{basename}-detail',
            initkwargs={'suffix': 'Instance'}
        ),
        # Dynamically generated routes.
        # Generated using @action or @link decorators on methods of the viewset.
        Route(
            url=r'^{prefix}/{lookup}/{methodname}{trailing_slash}$',
            mapping={
                '{httpmethod}': '{methodname}',
            },
            name='{basename}-{methodnamehyphen}',
            initkwargs={}
        ),
    ]
