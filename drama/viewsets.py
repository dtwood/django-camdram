from collections import namedtuple
from django.views.generic import DeleteView
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import viewsets, routers, permissions
from rest_framework.renderers import JSONRenderer, YAMLRenderer, BrowsableAPIRenderer, TemplateHTMLRenderer, StaticHTMLRenderer, XMLRenderer
from rest_framework.decorators import link, detail_route, permission_classes, api_view
from rest_framework.response import Response
from rest_framework.permissions import DjangoModelPermissions, DjangoObjectPermissions, BasePermission
from rest_framework.exceptions import MethodNotAllowed
from drama import serializers, models, views, forms, feeds
from drama.models import LogItem
from django.utils import timezone
from django.contrib import auth
from django.db.models import signals
from django.db import transaction
import reversion

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
        if request.user.has_perm('drama.add_' + self.model.class_name()):
            view = views.MyCreateView.as_view(model=self.model, model_name=self.model.class_name(), form_class = self.form)
            return view(request, *args, **kwargs)
        #Logging in MyCreateView
        else:
            raise PermissionDenied
    
    @detail_route(methods=['GET', 'POST'])
    @transaction.atomic()
    def edit(self, request, slug, *args, **kwargs):
        template_name = 'drama/' + self.model.__name__.lower() +'_form.html'
        item = get_object_or_404(self.model, slug=slug)
        temp_item = get_object_or_404(self.model, pk=item.pk)
        if request.user.has_perm('drama.change_' + item.class_name(), item):
            if request.method == 'GET':
                form = self.form(instance=item)
                data = {'content_form':form,
                        'object':item,
                        'current_pagetype': item.class_name(),
                        }
                return Response(data=data, template_name=template_name)
            elif request.method == 'POST':
                form = self.form(request.POST, request.FILES, instance=temp_item)
                if form.is_valid():
                    form.save()
                    log_item = LogItem(cat='EDIT', datetime=timezone.now(), user=self.request.user, content_object=item, desc='')
                    log_item.save()
                    return redirect(item.get_absolute_url())
                else:
                    data = {'content_form':form,
                            'object':item,
                            'current_pagetype': item.class_name(),
                            }
                    return Response(data=data, template_name=template_name)
            else:
                raise MethodNotAllowed
        else:
            raise PermissionDenied

    @detail_route(methods=['GET','POST'])
    @transaction.atomic()
    def remove(self, request, slug, *args, **kwargs):
        item = get_object_or_404(self.model, slug=slug)
        if request.user.has_perm('drama.change_' + self.model.class_name(), item):
            view = views.MyDeleteView.as_view(model=self.model, success_url="/")
            return view(request, slug=slug, *args, **kwargs)
        #Logging in MyDeleteView
        else:
            raise PermissionDenied

    @detail_route(methods=['GET','POST'])
    @transaction.atomic()
    def approve(self, request, slug, *args, **kwargs):
        item = get_object_or_404(self.model, slug=slug)
        if request.user.has_perm('drama.approve_' + item.class_name(), item):
            item.approve()
            log_item = LogItem(cat='APPROVE', datetime=timezone.now(), user=request.user, content_object=item, desc='Approved')
            log_item.save()
            return redirect(item.get_absolute_url())
        else:
            raise PermissionDenied

    @detail_route(methods=['GET'])
    @transaction.atomic()
    def unapprove(self, request, slug, *args, **kwargs):
        item = get_object_or_404(self.model, slug=slug)
        if request.user.has_perm('drama.approve_' + item.class_name(), item):
            item.unapprove()
            log_item = LogItem(cat='APPROVE', datetime=timezone.now(), user=request.user, content_object=item, desc='Unapproved')
            log_item.save()
            return redirect(item.get_absolute_url())
        else:
            raise PermissionDenied

    def list(self, request, *args, **kwargs):
        self.queryset = self.queryset.approved()
        response = super(ObjectViewSet, self).list(request, *args, **kwargs)
        if request.accepted_renderer.format == 'html':
            response.template_name = "drama/" + self.model.__name__.lower() + "_list.html"
            response.data = {'object_list': self.object_list, 'current_pagetype': self.model.class_name()}
        return response

    def retrieve(self, request, slug, *args, **kwargs):
        response = super(ObjectViewSet, self).retrieve(request, slug=slug, *args, **kwargs)
        if self.object.approved or request.user.has_perm('drama.change_' + self.object.class_name(), self.object) or request.user.has_perm('drama.approve_' + self.object.class_name(), self.object):
            if request.accepted_renderer.format == 'html':
                response.template_name = "drama/" + self.model.__name__.lower() + "_detail.html"
                can_edit = request.user.has_perm('drama.change_' + self.object.class_name(), self.object)
                response.data = {'object': self.object, 'current_pagetype': self.object.class_name(), 'can_edit':  can_edit}
            return response
        else:
            raise PermissionDenied

    @detail_route(methods=['GET', 'POST'])
    @transaction.atomic()
    def admins(self, request, slug, *args, **kwargs):
        item = get_object_or_404(self.model, slug=slug)
        if request.user.has_perm('change_' + item.class_name(), item):
            if request.method == "GET":
                context = {
                    'users': item.get_admins(),
                    'pending_users': item.get_pending_admins(),
                    'new_admin_form': forms.AdminForm(),
                    'parent': item,
                    'model_name': item.class_name(),
                }
                return render(request, 'drama/change_admins.html', context)
            elif request.method == "POST":
                form = forms.AdminForm(request.POST)
                if form.is_valid():
                    item.add_admin(form.cleaned_data['email'])
                    log_item = LogItem(cat='ADMIN', datetime=timezone.now(), user=request.user, content_object=item, desc='Added {0}'.format(form.cleaned_data['email']))
                    log_item.save()
                    signals.post_save.send(sender=item.__class__, instance=item, created=False, raw=False, using=None, update_fields=None)
                    return redirect(item.get_absolute_url())
                else:
                    context = {
                        'users': item.get_admins(),
                        'pending_users': item.get_pending_admins(),
                        'new_admin_form': form,
                        'parent': item,
                        'model_name': item.class_name(),
                    }
                    return render(request, 'drama/change_admins.html', context)
            elif request.method == "DELETE":
                username = request.DATA['username']
                try:
                    user = auth.get_user_model().objects.filter(username=username)[0]
                    item.revoke_admin(user)
                    log_item = LogItem(cat='ADMIN', datetime=timezone.now(), user=request.user, content_object=item, desc='Removed {0}'.format(user.email))
                    log_item.save()
                    signals.post_save.send(sender=item.__class__, instance=item, created=False, raw=False, using=None, update_fields=None)
                except IndexError:
                    pass
                return redirect(item.get_admins_url())
            else:
                return redirect(item.get_absolute_url())
        else:
            raise PermissionDenied

    @detail_route(methods=['POST'])
    @transaction.atomic()
    def revoke_admin(self, request, slug, *args, **kwargs):
        item = get_object_or_404(self.model, slug=slug)
        if request.user.has_perm('change_' + item.class_name(), item):
            username = request.DATA['username']
            try:
                user = auth.get_user_model().objects.filter(username=username)[0]
                item.revoke_admin(user)
                log_item = LogItem(cat='ADMIN', datetime=timezone.now(), user=request.user, content_object=item, desc='Removed {0}'.format(user.email))
                log_item.save()
                signals.post_save.send(sender=item.__class__, instance=item, created=False, raw=False, using=None, update_fields=None)
            except IndexError:
                pass
            return redirect(item.get_admins_url())
        else:
            raise PermissionDenied

    @detail_route(methods=['POST'])
    @transaction.atomic()
    def revoke_pending_admin(self, request, slug, *args, **kwargs):
        item = get_object_or_404(self.model, slug=slug)
        if request.user.has_perm('change_' + item.class_name(), item):
            email = request.DATA['email']
            item.remove_pending_admin(email)
            log_item = LogItem(cat='ADMIN', datetime=timezone.now(), user=request.user, content_object=item, desc='Removed {0}'.format(email))
            log_item.save()
            signals.post_save.send(sender=item.__class__, instance=item, created=False, raw=False, using=None, update_fields=None)
            return redirect(item.get_admins_url())
        else:
            raise PermissionDenied



class OrganizationViewSet(ObjectViewSet):
    @detail_route(methods=['GET', 'POST'])
    @transaction.atomic()
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
                    log_item = LogItem(cat='EDIT', datetime=timezone.now(), user=request.user, content_object=parent, desc='Changed Applications')
                    log_item.save()
                    signals.post_save.send(sender=parent.__class__, instance=parent, created=False, raw=False, using=None, update_fields=None)
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

    @detail_route(methods=['GET'])
    def ical(self, request, slug, *args, **kwargs):
        return feeds.SubCal(model=self.model)(request, slug=slug)
        
        
class RoleViewSet(ObjectViewSet):
    queryset = models.Role.objects.all()
    serializer_class = serializers.RoleSerializer
    model = models.Role
    form = forms.RoleForm

    @detail_route(methods=['GET'])
    def feed(self, request, *args, slug=None, **kwargs):
        return feeds.RoleFeed()(request, slug=slug)


class PersonViewSet(ObjectViewSet):
    queryset = models.Person.objects.all()
    serializer_class = serializers.PersonSerializer
    model = models.Person
    form = forms.PersonForm

    @detail_route(methods=['GET'])
    @transaction.atomic()
    def link(self, request, slug, *args, **kwargs):
        person = get_object_or_404(self.model, slug=slug)
        user = request.user
        if person.user is not None:
            raise PermissionDenied
        else:
            log_item = LogItem(cat='EDIT', datetime=timezone.now(), user=request.user, content_object=person, desc='Linked Person')
            log_item.save()
            signals.post_save.send(sender=person.__class__, instance=person, created=False, raw=False, using=None, update_fields=None)
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

    @detail_route(methods=['POST'])
    @transaction.atomic()
    def add_cast(self, request, slug, *args, **kwargs):
        show = get_object_or_404(self.model, slug=slug)
        if request.method == "POST":
            if request.user.has_perm('drama.change_show', show):
                form = forms.CastForm(request.POST)
                if form.is_valid():
                    character = get_object_or_404(models.Role,name='Character')
                    name = form.cleaned_data['role']
                    person = form.cleaned_data['person']
                    r = models.RoleInstance(name=name, show=show,person=person,role=character)
                    r.save()
                    log_item = LogItem(cat='EDIT', datetime=timezone.now(), user=request.user, content_object=show, desc='Added cast member: {0}'.format(person.name))
                    log_item.save()
                    signals.post_save.send(sender=show.__class__, instance=show, created=False, raw=False, using=None, update_fields=None)
                return redirect(show.get_absolute_url())
            else:
                raise PermissionDenied
        else:
            return redirect(show.get_absolute_url())


    @detail_route(methods=['POST'])
    @transaction.atomic()
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
                    log_item = LogItem(cat='EDIT', datetime=timezone.now(), user=request.user, content_object=show, desc='Added band member: {0}'.format(person.name))
                    log_item.save()
                    signals.post_save.send(sender=show.__class__, instance=show, created=False, raw=False, using=None, update_fields=None)
                return redirect(show.get_absolute_url())
            else:
                raise PermissionDenied
        else:
            return redirect(show.get_absolute_url())


    @detail_route(methods=['POST'])
    @transaction.atomic()
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
                    log_item = LogItem(cat='EDIT', datetime=timezone.now(), user=request.user, content_object=show, desc='Added production team member: {0}'.format(person.name))
                    log_item.save()
                    signals.post_save.send(sender=show.__class__, instance=show, created=False, raw=False, using=None, update_fields=None)
                return redirect(show.get_absolute_url())
            else:
                raise PermissionDenied
        else:
            return redirect(show.get_absolute_url())

    @detail_route(methods=['POST'])
    @transaction.atomic()
    def role_reorder(self, request, slug, *args, **kwargs):
        show = get_object_or_404(self.model, slug=slug)
        if request.user.has_perm('drama.change_show', show):
            for index, item_id in enumerate(request.POST.getlist('role[]')):
                item = get_object_or_404(models.RoleInstance, id=int(str(item_id)))
                if not item.show == show:
                    raise PermissionDenied
                item.sort = index
                item.save()
            log_item = LogItem(cat='EDIT', datetime=timezone.now(), user=request.user, content_object=show, desc='Reordered Roles')
            log_item.save()
            signals.post_save.send(sender=show.__class__, instance=show, created=False, raw=False, using=None, update_fields=None)
            return HttpResponse('')
        else:
            raise PermissionDenied

    @detail_route(methods=['POST'])
    @transaction.atomic()
    def remove_role(self, request, slug, *args, **kwargs):
        show = get_object_or_404(models.Show, slug=slug)
        role = get_object_or_404(models.RoleInstance, id=request.POST['role-id'])
        if role.show != show:
            raise Http404
        if request.user.has_perm('drama.change_show', show):
            log_item = LogItem(cat='EDIT', datetime=timezone.now(), user=request.user, content_object=show, desc='Removed company member: {0}'.format(role.person.name))
            log_item.save()
            role.delete()
            signals.post_save.send(sender=show.__class__, instance=show, created=False, raw=False, using=None, update_fields=None)
            return redirect(show.get_absolute_url())
        else:
            raise PermissionDenied

    @transaction.atomic()
    def related_edit(self, request, model, form, slug, *args, **kwargs):
        show = get_object_or_404(models.Show, slug=slug)
        template_name = 'drama/' + model.__name__.lower() + '_form.html'
        if request.user.has_perm('drama.change_show', show):
            try:
                item = model.objects.filter(show__slug=slug)[0]
                if request.method == 'GET':
                    bound_form = form(instance=item, parent=show, parent_name='show')
                    data = {'content_form': bound_form, 'parent': show}
                    return Response(data=data, template_name=template_name)
                elif request.method == 'POST':
                    bound_form = form(request.POST, request.FILES, instance=item, parent=show, parent_name='show')
                    if bound_form.is_valid():
                        bound_form.save()
                        log_item = LogItem(cat='EDIT', datetime=timezone.now(), user=request.user, content_object=show, desc='Changed {0}'.format(item.__class__.__name__))
                        log_item.save()
                        signals.post_save.send(sender=show.__class__, instance=show, created=False, raw=False, using=None, update_fields=None)
                        return redirect(show.get_absolute_url())
                    else:
                        data = {'content_form': bound_form, 'parent': show}
                        return Response(data=data, template_name=template_name)
                else:
                    raise MethodNotAllowed
            except IndexError:
                if request.method == 'GET':
                    bound_form = form(parent=show, parent_name='show')
                    data = {'content_form': bound_form, 'parent': show}
                    return Response(data=data, template_name=template_name)
                elif request.method == 'POST':
                    bound_form = form(request.POST, request.FILES, parent=show, parent_name='show')
                    if bound_form.is_valid():
                        bound_form.save()
                        log_item = LogItem(cat='EDIT', datetime=timezone.now(), user=request.user, content_object=show, desc='Added {0}'.format(model.__name__))
                        log_item.save()
                        signals.post_save.send(sender=show.__class__, instance=show, created=False, raw=False, using=None, update_fields=None)
                        return redirect(show.get_absolute_url())
                    else:
                        data = {'content_form': bound_form, 'parent': show}
                        return Response(data=data, template_name=template_name)
                else:
                    raise MethodNotAllowed
        else:
            raise PermissionDenied
    
    @transaction.atomic()
    def related_remove(self, request, model, slug, *args, **kwargs):
        show = get_object_or_404(models.Show, slug=slug)
        if request.user.has_perm('drama.change_show', show):
            try:
                item = model.objects.filter(show__slug=slug)[0]
                def on_success():
                    signals.post_save.send(sender=show.__class__, instance=show, created=False, raw=False, using=None, update_fields=None)
                    log_item = LogItem(cat='DELETE', datetime=timezone.now(), user=request.user, content_object=show, desc='Removed {0}'.format(item.__class__.__name__))
                    log_item.save()
                view = views.MyDeleteView.as_view(model=model, success_url=show.get_absolute_url(), on_success=on_success)
                return view(request, pk=item.pk, *args, **kwargs)
            except IndexError:
                raise Http404
        else:
            raise PermissionDenied

    @detail_route(methods=['GET','POST'])
    def technical(self, request, slug):
        return self.related_edit(request, models.TechieAd, forms.TechieAdForm, slug) 

    @detail_route(methods=['GET','POST'])
    def remove_technical(self, request, slug):
        return self.related_remove(request, models.TechieAd, slug) 

    @detail_route(methods=['GET','POST'])
    def auditions(self, request, slug):
        return self.related_edit(request, models.Audition, forms.AuditionForm, slug) 

    @detail_route(methods=['GET','POST'])
    def remove_auditions(self, request, slug):
        return self.related_remove(request, models.Audition, slug) 

class DramaRouter(routers.DefaultRouter):
    routes = [
        # List route.
        routers.Route(
            url=r'^{prefix}{trailing_slash}$',
            mapping={
                'get': 'list',
                #'post': 'create'
            },
            name='{basename}-list',
            initkwargs={'suffix': 'List'}
        ),
        # Form-based create route
        routers.Route(
            url=r'^{prefix}/new{trailing_slash}$',
            mapping={
                'get': 'new',
                'post': 'new',
                },
                name='{basename}-new',
                initkwargs={},
                ),
        # Detail route.
        routers.Route(
            url=r'^{prefix}/{lookup}{trailing_slash}$',
            mapping={
                'get': 'retrieve',
                #'put': 'update',
                #'patch': 'partial_update',
                #'delete': 'destroy'
            },
            name='{basename}-detail',
            initkwargs={'suffix': 'Instance'}
        ),
        # Dynamically generated routes.
        # Generated using @detail_route or @link decorators on methods of the viewset.
        routers.DynamicDetailRoute(
            url=r'^{prefix}/{lookup}/{methodname}{trailing_slash}$',
            name='{basename}-{methodnamehyphen}',
            initkwargs={}
        ),
    ]
