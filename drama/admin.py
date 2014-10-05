from django.contrib import admin
from drama.models import *
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User


class PerformanceInline(admin.TabularInline):
    model = Performance
    extra = 1
    raw_id_fields = ['venue']


class RoleInline(admin.TabularInline):
    model = RoleInstance
    extra = 5
    verbose_name = 'Role'
    raw_id_fields = ['role','person']


class TechieAdInline(admin.TabularInline):
    model = TechieAdRole
    extra = 5
    verbose_name = 'Role'
    raw_id_fields = ['role']


class AuditionInline(admin.TabularInline):
    model = AuditionInstance
    extra = 1


@admin.register(Show)
class ShowAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {
         'fields': ['name', 'author', 'desc', 'societies', 'image']}),
        ('Booking info', {
         'fields': ['book', 'prices'], 'classes': ['collapse']}),
        ('Advanced Settings', {'fields': ['slug'], 'classes': ['collapse']})
    ]
    inlines = [PerformanceInline, RoleInline]
    list_display = ['name', 'opening_night', 'slug', 'id', 'approved']
    search_fields = ['name']


@admin.register(TechieAd)
class TechieAdAdmin(admin.ModelAdmin):
    list_display = ['show', 'contact', 'deadline']
    inlines = [TechieAdInline]
    search_fields = ['show']
    raw_id_fields = ['show']


@admin.register(Audition)
class AuditionAdmin(admin.ModelAdmin):
    list_display = ['show', 'contact']
    inlines = [AuditionInline]
    search_fields = ['show']
    raw_id_fields = ['show']

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ['name','num_shows','user_email',]
    search_fields = ['name',]
    raw_id_fields = ['user']

    
@admin.register(Venue)
class DramaObjectAdmin(admin.ModelAdmin):
    list_display = ['name','approved']
    search_fields = ['name']
    list_filter = ['approved']
    
@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name','cat','approved']
    search_fields = ['name']
    list_filter = ['cat','approved']
    
@admin.register(Society)
class SocietyAdmin(admin.ModelAdmin):
    list_display = ['name','shortname','approved']
    search_fields = ['name','shortname']
    list_filter = ['approved']
    
@admin.register(ShowApplication)
class ShowApplicationAdmin(admin.ModelAdmin):
    list_display = ['name','show','deadline']
    search_fields = ['name', 'show__name']
    raw_id_fields = ['show']

@admin.register(SocietyApplication)
class SocietyApplicationAdmin(admin.ModelAdmin):
    list_display = ['name','society', 'deadline']
    search_fields = ['name', 'society__name', 'society__shortname']
    raw_id_fields = ['society']

@admin.register(VenueApplication)
class VenueApplicationAdmin(admin.ModelAdmin):
    list_display = ['name','venue','deadline']
    search_fields = ['name', 'venue__name']
    raw_id_fields = ['venue']

@admin.register(TermDate)
class TermDateAdmin(admin.ModelAdmin):
    list_display = ['__str__','start']
    list_filter = ['term','year']
    list_editable = ['start']

@admin.register(ApprovalQueueItem)
class ApprovalQueueAdmin(admin.ModelAdmin):
    list_display = ['content_object']

@admin.register(LogItem)
class LogAdmin(admin.ModelAdmin):
    list_display = ['object_link', 'cat', 'desc', 'user_email','datetime']
    list_filter = ['cat','user__email']
    list_display_links = ['cat']
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
