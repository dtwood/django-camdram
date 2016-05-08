from django.conf.urls import patterns, url, include
from haystack.views import SearchView, search_view_factory
from drama.views import autocomplete
from drama.forms import CamdramSearchForm

urlpatterns = [
    url(r'^$', search_view_factory(view_class=SearchView, form_class=CamdramSearchForm), name='haystack_search'),
    url(r'^autocomplete$', autocomplete, name='haystack_autocomplete'),
]
