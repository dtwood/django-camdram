import autocomplete_light
from drama.models import Society, Venue
from django.core.urlresolvers import reverse


class SocietyAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['name', 'shortname']

class VenueAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['name']
    
autocomplete_light.register(Society, SocietyAutocomplete, add_another_url_name='new', add_another_url_kwargs={'model_name':'societies'}, field_name='society')

autocomplete_light.register(Venue, VenueAutocomplete, add_another_url_name='new', add_another_url_kwargs={'model_name':'venues'}, field_name='venue')
