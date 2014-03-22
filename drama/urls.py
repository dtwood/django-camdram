from django.conf.urls import patterns, url, include
from django.views.generic import TemplateView, ListView
from drama.models import Venue, Society
from drama import views

urlpatterns = patterns('',
                       url(r'^$', views.index, name='home'),
                       url(r'^diary/?$', views.diary, name='diary'),
                       url(r'^search/?', include('drama.haystack_urls'), name='search'),
                       url(r'^about/?$', TemplateView.as_view(template_name="drama/about.html"), name='about'),
                       url(r'^development/?$', views.development, name='development'),
                       url(r'^contact-us/?$', views.contact_us, name='contact-us'),
                       url(r'^privacy/?$', TemplateView.as_view(template_name="drama/privacy.html"), name='privacy'),
                       url(r'^shows/(?P<slug>[^/]*)', views.show, name='show'),
                       url(r'^people/(?P<slug>[^/]*)', views.person, name='person'),
                       url(r'^roles/(?P<slug>[^/]*)', views.role, name='role'),
                       url(r'^venues/?$',ListView.as_view(model=Venue), name='venues'),
                       url(r'^venues/(?P<slug>[^/]*)', views.venue, name='venue'),
                       url(r'^societies/?$', ListView.as_view(model=Society), name='societies'),
                       url(r'^societies/(?P<slug>[^/]*)', views.society, name='society'),
                       url(r'^vacancies/technical/?$', views.techieads, name='techie_ads'),
                       url(r'^vacancies/auditions/?$', views.auditions, name='auditions'),
                       url(r'^vacancies/auditions/diary/?$', views.auditions_diary, name='auditions_diary'),
                       url(r'^vacancies/applications/?$', views.applications, name='applications'),
                       url(r'^vacancies/technical/(?P<slug>[^/]*)', views.techieads_item, name='techieads_item'),
                       url(r'^vacancies/auditions/(?P<slug>[^/]*)', views.auditions_item, name='auditions_item'),
                       url(r'^vacancies/applications/(?P<slug>[^/]*)', views.applications_item, name='applications_item'),
                       url(r'^vacancies/(?P<show_slug>[^/]*)/(?P<role_slug>[^/]*)', views.ad_role, name='ad_role'),
                       
                       )
