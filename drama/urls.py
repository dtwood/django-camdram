import dal as dal
from django.contrib import auth
from django.conf.urls import patterns, url, include
from django.views.generic import TemplateView, ListView
from drama import viewsets, feeds, views
from rest_framework.routers import DefaultRouter
from registration.backends.default.views import ActivationView

router = viewsets.DramaRouter(trailing_slash=False)
router.register(r'roles', viewsets.RoleViewSet)
router.register(r'people', viewsets.PersonViewSet)
router.register(r'societies', viewsets.SocietyViewSet)
router.register(r'venues', viewsets.VenueViewSet)
router.register(r'shows', viewsets.ShowViewSet)
router.register(r'mailinglists', viewsets.EmailListViewSet)


vacancy_patterns = [
    url(r'^technical/$', views.techieads, name='technical'),
    url(r'^technical/feed/$', feeds.TechieAdFeed(), name='techiead_feed'),
    url(r'^auditions/$', views.auditions, name='auditions'),
    url(r'^auditions/diary/$', views.auditions_diary, name='auditions_diary'),
    url(r'^auditions/feed/$', feeds.AuditionFeed(), name='auditions_feed'),
    url(r'^applications/$', views.applications, name='applications'),
    url(r'^applications/feed/$', feeds.ApplicationFeed(), name='applications_feed'),
    url(r'^technical/(?P<slug>[^/]*)/$', views.techiead_item, name='techiead-item'),
    url(r'^auditions/(?P<slug>[^/]*)/$', views.audition_item, name='audition-item'),
    url(r'^applications/(?P<slug>[^/]*)/$', views.application_item, name='application-item'),
    url(r'^(?P<show_slug>[^/]*)/(?P<role_slug>[^/]*)/$', views.ad_role, name='ad_role'),
]


simple_register_patterns = [
    url(r'^activate/complete/$', TemplateView.as_view(template_name='registration/activation_complete.html'), name='registration_activation_complete'),
    # Activation keys get matched by \w+ instead of the more specific
    # [a-fA-F0-9]{40} because a bad activation key should still get to the view;
    # that way it can return a sensible "invalid key" message instead of a
    # confusing 404.
    url(r'^activate/(?P<activation_key>\w+)/$', ActivationView.as_view(), name='registration_activate'),
    url(r'^register/$', views.EmailRegistrationView.as_view(), name='registration_register'),
    url(r'^register/complete/$', TemplateView.as_view(template_name='registration/registration_complete.html'), name='registration_complete'),
    url(r'^register/closed/$', TemplateView.as_view(template_name='registration/registration_closed.html'), name='registration_disallowed'),
    url(r'', include('django.contrib.auth.urls')),
]


urlpatterns = [
    url(r'^$', views.index, name='home'),
    url(r'^', include(router.urls)),
    url(r'^auth/', include(simple_register_patterns)),
    url(r'^diary/$', views.diary, name='diary'),
    url(r'^diary_week$', views.diary_week, name='diary_week'),
    url(r'^diary/(?P<week>[-0-9]+)$', views.diary, name='diary'),
    url(r'^diary_jump$', views.diary_jump, name='diary_jump'),
    url(r'^search', include('drama.haystack_urls'), name='search'),
    url(r'^ical/', feeds.FullCal(), name='ical'),
    url(r'^about/$', TemplateView.as_view(template_name="drama/about.html"), name='about'),
    url(r'^development/$', views.development, name='development'),
    url(r'^contact-us/$', views.contact_us, name='contact-us'),
    url(r'^privacy/$', TemplateView.as_view(template_name="drama/privacy.html"), name='privacy'),
    url(r'^vacancies/', include(vacancy_patterns)),
    url(r'^show-admin/$', views.show_admin, name='show-admin'),
    url(r'^approvals/$', views.approval_queue, name='approvals'),
    url(r'^approvals/(?P<key>[0-9]*)/ignore$', views.approval_ignore, name='approval-ignore'),
    url(r'approvals/(?P<key>[0-9]*)/approve$', views.approval_approve, name='approval-approve'),
]
