from django.contrib import admin
from drama.models import *

class PerformanceInline(admin.TabularInline):
    model = Performance
    extra = 1

class RoleInline(admin.TabularInline):
    model = RoleInstance
    extra = 5
    verbose_name = 'Role'

class TechieAdInline(admin.TabularInline):
    model = TechieAdRole
    extra = 5
    verbose_name = 'Role'

class AuditionInline(admin.TabularInline):
    model = Audition
    extra = 1
    
class ShowAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name', 'author', 'desc', 'society', 'year', 'image']}),
        ('Booking info', {'fields': ['book','prices'], 'classes': ['collapse']}),
        ('Advanced Settings', {'fields': ['slug'], 'classes': ['collapse']})
        ]
    inlines = [PerformanceInline,RoleInline]
    list_display = ['name', 'opening_night', 'slug']

class TechieAdAdmin(admin.ModelAdmin):
    inlines = [TechieAdInline]

class AuditionAdmin(admin.ModelAdmin):
    inlines = [AuditionInline]
    
admin.site.register(Person)
admin.site.register(Venue)
admin.site.register(Show, ShowAdmin)
admin.site.register(Role)
admin.site.register(Society)
admin.site.register(TechieAd,TechieAdAdmin)
admin.site.register(AuditionAd,AuditionAdmin)
admin.site.register(SocietyApplication)
admin.site.register(VenueApplication)
admin.site.register(DirectorApplication)

