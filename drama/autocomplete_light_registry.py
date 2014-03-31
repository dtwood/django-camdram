import autocomplete_light
from drama.models import Society, Venue, Person, Role
from django.core.urlresolvers import reverse


class SocietyAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['name', 'shortname']


class VenueAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['name']


class PersonAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['name']


class RoleAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['name']
    
autocomplete_light.register(Society, SocietyAutocomplete, add_another_url_name='new', add_another_url_kwargs={
                            'model_name': 'societies'}, field_name='society')

autocomplete_light.register(Venue, VenueAutocomplete, add_another_url_name='new', add_another_url_kwargs={
                            'model_name': 'venues'}, field_name='venue')

autocomplete_light.register(Person, PersonAutocomplete, add_another_url_name='new', add_another_url_kwargs={
                            'model_name': 'people'}, field_name='person')

autocomplete_light.register(Role, RoleAutocomplete, add_another_url_name='new', add_another_url_kwargs={'model_name': 'roles'}, field_name='role', widget_attrs = {'data-widget-bootstrap': 'fill-field-bootstrap',})

autocomplete_light.register(RoleAutocomplete, name='cast', choices=Role.objects.filter(cat='cast'))

autocomplete_light.register(RoleAutocomplete, name='band', choices=Role.objects.filter(cat='band'))

autocomplete_light.register(RoleAutocomplete, name='prod', choices=Role.objects.filter(cat='prod'))
