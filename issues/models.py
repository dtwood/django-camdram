from django.db import models
from django.conf import settings
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from django.utils.html import escape
from django.core.mail import send_mail
from django.utils import timezone

class Issue(models.Model):
    name = models.CharField(max_length=200,blank=True)
    desc = models.TextField(blank=True)
    assigned_user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    active = models.BooleanField(default=False)
    email = models.EmailField()
    opened = models.DateTimeField()

    def send_response(self, sender, body):
        from_addr = 'issue-' + str(self.id) +'@' + settings.EMAIL_FROM_DOMAIN
        subject = '[' + settings.EMAIL_FROM_DOMAIN + ']Re: Support Request ' + str(self.id) +' (' + self.name + ')'
        send_mail(subject, body, from_addr, [self.email])
        message = Message(issue=self, sender=sender, body=body, recieved=timezone.now())
        message.save()
    send_response.alters_data=True
    
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
    sender = models.CharField(max_length=260)
    body = models.TextField()
    recieved = models.DateTimeField()

