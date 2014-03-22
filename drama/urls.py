from django.conf.urls import patterns, url, include
from django.views.generic import TemplateView, ListView
from drama.models import *
from drama import views, contexts

#pass in with a slug, model_name, model, form, template and get_context and get apropriate views
#model_name and slug should be captured, the others passed in a dict
#get_context and template are used only when displaying a single item
#model_name is only for url reversal
object_patterns = patterns('drama.views',
                           url(r'^$', 'display', name='display'),
                           url(r'^new$', 'new', name='new'),
                           url(r'^edit$', 'edit', name='edit'),
                           url(r'^remove$', 'remove', name='remove'),
                           )

redirector_patterns = patterns('drama.views',
                               url(r'^$', 'my_redirect', name='item'),
                               url(r'^', include(object_patterns)),
                               )

vacancy_patterns = patterns('drama.views',
                       url(r'^technical/$', 'techieads', name='technical'),
                       url(r'^auditions/$', 'auditions', name='auditions'),
                       url(r'^auditions/diary/$', 'auditions_diary', name='auditions_diary'),
                       url(r'^applications/$', 'applications', name='applications'),
                       url(r'^(?P<model_name>technical)/(?P<slug>[^/]*)', include(redirector_patterns), {'model': TechieAd,'form': None,}),
                       url(r'^(?P<model_name>auditions)/(?P<slug>[^/]*)', include(redirector_patterns), {'model': Audition,'form': None,}),
                       #society and venue applications must happen elsewhere
                       url(r'^(?P<model_name>applications)/(?P<slug>[^/]*)', include(redirector_patterns), {'model': ShowApplication,'form': None,}),
                       url(r'^(?P<show_slug>[^/]*)/(?P<role_slug>[^/]*)', 'ad_role', name='ad_role'),
                        )

list_patterns = patterns('drama.views',
                         url(r'^$', 'list', name='list'),
                         url(r'^(?P<slug>[^/]*)/', include(object_patterns)),
                         )

urlpatterns = patterns('',
                       url(r'^$', views.index, name='home'),
                       url(r'^diary/$', views.diary, name='diary'),
                       url(r'^search/', include('drama.haystack_urls'), name='search'),
                       url(r'^about/$', TemplateView.as_view(template_name="drama/about.html"), name='about'),
                       url(r'^development/?$', views.development, name='development'),
                       url(r'^contact-us/?$', views.contact_us, name='contact-us'),
                       url(r'^privacy/?$', TemplateView.as_view(template_name="drama/privacy.html"), name='privacy'),
                       url(r'^shows/(?P<slug>[^/]*)', views.show, name='show'),
                       url(r'^people/(?P<slug>[^/]*)', views.person, name='person'),
                       url(r'^roles/(?P<slug>[^/]*)', views.role, name='role'),
                       url(r'^(?P<model_name>venues)/', include(list_patterns), {'model':Venue, 'form':None, 'get_context':contexts.venue}),
                       url(r'^(?P<model_name>societies)/', include(list_patterns), {'model':Society, 'form':None, 'get_context':contexts.society}),
                       url(r'^vacancies/',include(vacancy_patterns)),
                       
                       )
