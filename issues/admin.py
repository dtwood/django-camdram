from django.contrib import admin
from issues.models import *

# Register your models here.

class MessageInline(admin.TabularInline):
    model = Message
    extra = 1

class IssueAdmin(admin.ModelAdmin):
    inlines = [MessageInline]

admin.site.register(Issue, IssueAdmin)
