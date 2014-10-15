from __future__ import absolute_import

import os

from celery import Celery
from celery.schedules import crontab

from django.conf import settings
import drama

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'camdram.settings')

app = Celery('camdram', broker='amqp://guest@localhost//')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

CELERYBEAT_SCHEDULE = {
    'social-news-update': {
        'task':'camdram-update-posts',
        'schedule': crontab(minute='*/15'),
        }
    }


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

@app.task(bind=True, name='camdram.update-posts')
def update_posts(self):
    for ven in drama.models.Venue.objects.all():
        ven.update_posts()
    for soc in drama.models.Society.objects.all():
        soc.update_posts()
