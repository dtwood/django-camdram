from django.conf.urls import patterns, url

from drama import views

urlpatterns = patterns('',
                       url(r'^$', views.index, name='index'),
                       url(r'^shows/(?P<slug>[^/]*)', views.show, name='show'),
                       url(r'^people/(?P<slug>[^/]*)', views.person, name='person'),
                       url(r'^roles/(?P<slug>[^/]*)', views.role, name='role'),
                       url(r'^venues/(?P<slug>[^/]*)', views.venue, name='venue'),
                       url(r'^societies/(?P<slug>[^/]*)', views.society, name='society'),
                       url(r'^vacancies/technical$', views.techieads, name='techie_ads'),
                       url(r'^vacancies/auditions$', views.auditions, name='auditions'),
                       url(r'^vacancies/applications$', views.applications, name='applications'),
                       url(r'^vacancies/technical/(?P<slug>[^/]*)', views.techieads_show, name='techieads_show'),
                       url(r'^vacancies/auditions/(?P<slug>[^/]*)', views.auditions_show, name='auditions_show'),
                       url(r'^vacancies/applications/(?P<slug>[^/]*)', views.applications_show, name='applications_show'),
                       url(r'^vacancies/(?P<show_slug>[^/]*)/(?P<role_slug>[^/]*)', views.ad_role, name='ad_role'),
                       
                       )
