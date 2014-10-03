from django.db import models
from django.conf import settings
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from django.utils.html import escape

class Issue(models.Model):
    name = models.CharField(max_length=200,blank=True)
    desc = models.TextField(blank=True)
    assigned_user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    active = models.BooleanField(default=False)
    email = models.EmailField()
    opened = models.DateTimeField()

    def send_response(self, sender, body):
        pass #TODO

    class Meta:
        ordering = ['-opened']
        permissions = (
            ('view_issues', 'Can view issues'),
            )

    def get_absolute_url(self):
        return reverse('issues:detail', kwargs={'key': self.id})

    def get_link(self):
        return mark_safe('<a href="{0}">{1}</a>'.format(self.get_absolute_url(), escape(self.name)))

class Message(models.Model):
    issue = models.ForeignKey(Issue)
    sender = models.TextField()
    recieved = models.DateTimeField()

