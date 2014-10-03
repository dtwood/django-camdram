from django.conf.urls import patterns, url, include

urlpatterns = patterns('issues.views',
                       url(r'^$', 'list', name='list'),
                       url(r'^(?P<key>[0-9]*)$','detail', name='detail'),
                       url(r'^(?P<key>[0-9]*)/close$','close', name='close'),
                       url(r'^(?P<key>[0-9]*)/claim$','claim', name='claim'),
                       )
