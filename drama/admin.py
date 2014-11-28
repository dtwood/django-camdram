from django.contrib import admin
from drama import models
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.shortcuts import redirect
import reversion


class OrphanFilter(admin.SimpleListFilter):
    title = 'Is orphaned'
    parameter_name = 'orphan'

    def lookups(self, request, model_admin):
        return (('true', 'True'),('false', 'False'))

    def queryset(self, request, queryset):
        if self.value() == 'true':
            return queryset.filter(num_shows=0)
        if self.value() == 'false':
            return queryset.exclude(num_shows=0)

class PerformanceInline(admin.TabularInline):
    model = models.Performance
    extra = 0
    raw_id_fields = ['venue']


class RoleInline(admin.TabularInline):
    model = models.RoleInstance
    extra = 0
    verbose_name = 'Role'
    fields = ['name', 'role', 'person', 'sort']
    raw_id_fields = ['role','person']


class TechieAdInline(admin.TabularInline):
    model = models.TechieAdRole
    extra = 0
    verbose_name = 'Role'
    raw_id_fields = ['role']


class AuditionInline(admin.TabularInline):
    model = models.AuditionInstance
    extra = 0

class ShowApplicationInline(admin.StackedInline):
    model = models.ShowApplication
    extra = 0


class SocietyApplicationInline(admin.StackedInline):
    model = models.SocietyApplication
    extra = 0


class VenueApplicationInline(admin.StackedInline):
    model = models.VenueApplication
    extra = 0

class NameAliasInline(admin.TabularInline):
    model = models.NameAlias
    extra = 0

@admin.register(models.Show)
class ShowAdmin(reversion.VersionAdmin):
    fieldsets = [
        (None, {
         'fields': ['name', 'author', 'desc', 'societies', 'image']}),
        ('Booking info', {
         'fields': ['book', 'prices'], 'classes': ['collapse']}),
        ('Advanced Settings', {'fields': ['slug'], 'classes': ['collapse']})
    ]
    inlines = [PerformanceInline, RoleInline, ShowApplicationInline]
    list_display = ['name', 'opening_night', 'slug', 'id', 'approved']
    search_fields = ['name']


@admin.register(models.TechieAd)
class TechieAdAdmin(admin.ModelAdmin):
    list_display = ['show', 'contact', 'deadline']
    inlines = [TechieAdInline]
    search_fields = ['show']
    raw_id_fields = ['show']


@admin.register(models.Audition)
class AuditionAdmin(admin.ModelAdmin):
    list_display = ['show', 'contact']
    inlines = [AuditionInline]
    search_fields = ['show']
    raw_id_fields = ['show']

@admin.register(models.Person)
class PersonAdmin(reversion.VersionAdmin):
    actions = ['merge_people']
    list_display = ['name','num_shows','user_email',]
    list_filter = [OrphanFilter]
    search_fields = ['name',]
    raw_id_fields = ['user']
    inlines = [NameAliasInline]

    def merge_people(self, request, queryset):
        new_queryset = queryset.order_by('-num_shows')
        print(new_queryset)
        keep = new_queryset[0]
        count = new_queryset.count()
        for person in new_queryset[1:]:
            for role in person.roleinstance_set.all():
                role.person = keep
                role.save()
            models.NameAlias(person=keep, name=person.name).save()
            person.delete()
        self.message_user(request, '{} people successfully merged'.format(count))
        return redirect(keep.get_admin_interface_url())

@admin.register(models.Venue)
class VenueAdmin(reversion.VersionAdmin):
    list_display = ['name','approved']
    search_fields = ['name']
    list_filter = ['approved']
    inlines = [VenueApplicationInline]
    
@admin.register(models.Role)
class RoleAdmin(reversion.VersionAdmin):
    list_display = ['name','cat','approved']
    search_fields = ['name']
    list_filter = ['cat','approved']
    
@admin.register(models.Society)
class SocietyAdmin(reversion.VersionAdmin):
    list_display = ['name','shortname','approved']
    search_fields = ['name','shortname']
    list_filter = ['approved']
    inlines = [SocietyApplicationInline]

@admin.register(models.TermDate)
class TermDateAdmin(reversion.VersionAdmin):
    list_display = ['__str__','start']
    list_filter = ['term','year']
    list_editable = ['start']

@admin.register(models.ApprovalQueueItem)
class ApprovalQueueAdmin(admin.ModelAdmin):
    list_display = ['content_object']

@admin.register(models.LogItem)
class LogAdmin(admin.ModelAdmin):
    fields = ('object_link', 'cat', 'desc', 'user_email', 'datetime')
    readonly_fields = ('object_link', 'cat', 'desc', 'user_email', 'datetime')
    list_display = ['object_link', 'cat', 'desc', 'user_email','datetime']
    list_filter = ['cat','user__email', 'content_type']
    list_display_links = ['cat']

    def has_delete_permission(self, request, obj=None):
        #Disable delete
        return False

    def has_add_permission(self, request):
        #Disable creating new log entries
        return False

    def get_actions(self, request):
        #Disable delete
        actions = super(LogAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

admin.site.unregister(User)

class CustomUserAdmin(UserAdmin):
    def __init__(self, *args, **kwargs):
        result = super(CustomUserAdmin, self).__init__(*args, **kwargs)
        self.list_display = self.list_display + ('log_link',)

    def log_link(self, obj):
        return '<a href="{0}">Logs</a>'.format('/admin/drama/logitem/?user_id__exact={0}'.format(obj.id))
    log_link.allow_tags = True
    log_link.short_description = 'Logs'

admin.site.register(User, CustomUserAdmin)
admin.site.register(models.EmailList)
