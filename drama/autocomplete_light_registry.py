import autocomplete_light
from drama.models import Society
from django.core.urlresolvers import reverse


class SocietyAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['name', 'shortname']

autocomplete_light.register(Society, SocietyAutocomplete, add_another_url_name='new', add_another_url_kwargs={'model_name':'societies'}, field_name='society')
