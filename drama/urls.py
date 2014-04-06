import autocomplete_light
autocomplete_light.autodiscover()
from django.contrib import auth
from django.conf.urls import patterns, url, include
from django.views.generic import TemplateView, ListView
from drama.models import *
from drama import views, contexts
from drama.forms import *
from registration.backends.simple.views import RegistrationView as SimpleRegistrationView


# pass in with a slug, model_name, model, form, template and get_context and get apropriate views
# model_name and slug should be captured, the others passed in a dict
# get_context and template are used only when displaying a single item
# model_name is only for url reversal
object_patterns = patterns('drama.views',
                           url(r'^$', 'display', name='display'),
                           url(r'^edit$', 'edit', name='edit'),
                           url(r'^remove$', 'remove', name='remove'),
                           )

related_object_patterns  = patterns('drama.views',
                                    url(r'^edit$', 'related_edit', name='related_edit'),
                                    url(r'remove$', 'related_remove', name='related_remove'),
                                    )

redirector_patterns = patterns('drama.views',
                               url(r'^$', 'my_redirect', name='item'),
                               url(r'^', include(object_patterns)),
                               )

related_redirector_patterns = patterns('drama.views',
                               url(r'^$', 'my_redirect', name='item'),
                               url(r'^', include(related_object_patterns)),
                               )

vacancy_patterns = patterns('drama.views',
                            url(r'^technical/$', 'techieads',
                                name='technical'),
                            url(r'^auditions/$', 'auditions',
                                name='auditions'),
                            url(r'^auditions/diary/$', 'auditions_diary',
                                name='auditions_diary'),
                            url(r'^applications/$', 'applications',
                                name='applications'),
                            url(r'^(?P<model_name>technical)/(?P<slug>[^/]*)/',
                                include(related_redirector_patterns), {'model': TechieAd, 'form': TechieAdForm, }),
                            url(r'^(?P<model_name>auditions)/(?P<slug>[^/]*)/',
                                include(related_redirector_patterns), {'model': Audition, 'form': AuditionForm, }),
                            url(r'^(?P<model_name>applications)/(?P<slug>[^/]*)/',
                                include(redirector_patterns), {'model': Application, 'form': ApplicationForm, }),
                            url(r'^(?P<show_slug>[^/]*)/(?P<role_slug>[^/]*)/$',
                                'ad_role', name='ad_role'),
                            )

list_patterns = patterns('drama.views',
                         url(r'^$', 'list', name='list'),
                         url(r'^new$', 'new', name='new'),
                         url(r'^(?P<slug>[^/]+)/', include(object_patterns)),
                         )

show_patterns = patterns('drama.views',
                         url(r'(?P<slug>[^/]+)/applications/edit', 'application_edit', {'form': ShowApplicationFormset, 'prefix': 'show'}, name='applications_edit'),
                         url(r'(?P<slug>[^/]+)/(?P<submodel_name>technical)/', include(related_object_patterns), {'model': TechieAd, 'form': TechieAdForm, } ),
                         url(r'(?P<slug>[^/]+)/(?P<submodel_name>auditions)/', include(related_object_patterns), {'model': Audition, 'form': AuditionForm, } ),
                         url(r'(?P<slug>[^/]+)/remove_role/(?P<id>[^/]+)/', 'remove_role', name='remove_role'),
                         url(r'(?P<slug>[^/]+)/add_cast', 'add_cast', name='add_cast'),
                         url(r'(?P<slug>[^/]+)/add_band', 'add_band', name='add_band'),
                         url(r'(?P<slug>[^/]+)/add_prod', 'add_prod', name='add_prod'),
                         url(r'(?P<slug>[^/]+)/role_reorder', 'role_reorder', name='role_reorder'),
                         url(r'(?P<slug>[^/]+)/admins$', 'change_admins', name='change_admins'),
                         url(r'(?P<slug>[^/]+)/admins/revoke/(?P<username>[^/]+)$', 'revoke_admin', name='revoke_admin'),
                         url(r'^', include(list_patterns)),
                         )

venue_patterns = patterns('drama.views',
                         url(r'(?P<slug>[^/]+)/applications/edit', 'application_edit', {'form': VenueApplicationFormset, 'prefix': 'venue'}, name='applications_edit'),
                         url(r'(?P<slug>[^/]+)/admins$', 'change_admin_group', name='change_admins'),
                         url(r'(?P<slug>[^/]+)/admins/revoke/(?P<username>[^/]+)$', 'revoke_admin', name='revoke_admin'),
                         url(r'', include(list_patterns)),
                         )

society_patterns = patterns('drama.views',
                         url(r'(?P<slug>[^/]+)/applications/edit', 'application_edit', {'form': SocietyApplicationFormset, 'prefix': 'society'}, name='applications_edit'),
                         url(r'(?P<slug>[^/]+)/admins$', 'change_admin_group', name='change_admins'),
                         url(r'(?P<slug>[^/]+)/admins/revoke/(?P<username>[^/]+)$', 'revoke_admin', name='revoke_admin'),
                         url(r'', include(list_patterns)),
                         )

person_patterns = patterns('drama.views',
                           url(r'(?P<slug>[^/]+)/link', 'link_user', name='link_user'),
                           url(r'', include(list_patterns)),
                           )
simple_register_patterns = patterns('',
url(r'^register/$', views.EmailRegistrationView.as_view(), name='registration_register'),
url(r'^register/closed/$', TemplateView.as_view(template_name='registration/registration_closed.html'), name='registration_disallowed'),
(r'', include('django.contrib.auth.urls')),
)

urlpatterns = patterns('drama.views',
                       url(r'^$', views.index, name='home'),
                       url(r'^auth/', include(simple_register_patterns)),
                       url(r'^diary/$', views.diary, name='diary'),
                       url(r'^search/', include('drama.haystack_urls'),
                           name='search'),
                       url(r'^about/$',
                           TemplateView.as_view(template_name="drama/about.html"), name='about'),
                       url(r'^development/$', views.development,
                           name='development'),
                       url(r'^contact-us/$', views.contact_us,
                           name='contact-us'),
                       url(r'^privacy/$',
                           TemplateView.as_view(template_name="drama/privacy.html"), name='privacy'),
                       url(r'^(?P<model_name>shows)/', include(show_patterns),
                           {'model': Show, 'form': ShowForm, 'get_context': contexts.show}),
                       url(r'^(?P<model_name>people)/', include(person_patterns),
                           {'model': Person, 'form': PersonForm, 'get_context': contexts.person}),
                       url(r'^(?P<model_name>roles)/', include(list_patterns),
                           {'model': Role, 'form': RoleForm, 'get_context': contexts.role}),
                       url(r'^(?P<model_name>venues)/', include(venue_patterns),
                           {'model': Venue, 'form': VenueForm, 'get_context': contexts.venue}),
                       url(r'^(?P<model_name>societies)/', include(society_patterns),
                           {'model': Society, 'form': SocietyForm, 'get_context': contexts.society}),
                       url(r'^vacancies/', include(vacancy_patterns)),
                       url(r'autocomplete/',
                           include('autocomplete_light.urls')),
                       url(r'show-admin/$', 'show_admin', name='show-admin'), 
                       )
