from django.conf.urls import patterns, url, include
from issues import views

urlpatterns = [
    url(r'^$', views.list, name='list'),
    url(r'^(?P<key>[0-9]*)$', views.detail, name='detail'),
    url(r'^(?P<key>[0-9]*)/close$', views.close, name='close'),
    url(r'^(?P<key>[0-9]*)/claim$', views.claim, name='claim'),
]
