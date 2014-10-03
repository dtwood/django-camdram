from django.conf.urls import patterns, url, include

urlpatterns = patterns('issues.views',
                       url(r'^$', 'list', name='list'),
                       url(r'(?P<key>[0-9]*)','detail', name='detail'),
                       )
