from django.contrib import admin
from issues import models

# Register your models here.

class MessageInline(admin.TabularInline):
    model = models.Message
    extra = 1

class IssueAdmin(admin.ModelAdmin):
    inlines = [MessageInline]

admin.site.register(models.Issue, IssueAdmin)
