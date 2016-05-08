import dal
from drama.models import Society, Venue, Person, Role
from django.core.urlresolvers import reverse


class SocietyAutocomplete(dal.AutocompleteModelBase):
    search_fields = ['name', 'shortname']


class VenueAutocomplete(dal.AutocompleteModelBase):
    search_fields = ['name']


class PersonAutocomplete(dal.AutocompleteModelBase):
    search_fields = ['name', 'namealias__name']


class RoleAutocomplete(dal.AutocompleteModelBase):
    search_fields = ['name']
    
dal.register(Society, SocietyAutocomplete, add_another_url_name='society-new', field_name='society')
dal.register(Society, SocietyAutocomplete, add_another_url_name='society-new', field_name='societies')

dal.register(Venue, VenueAutocomplete, add_another_url_name='venue-new', field_name='venue')

dal.register(Person, PersonAutocomplete, add_another_url_name='person-new', field_name='person')

dal.register(Role, RoleAutocomplete, add_another_url_name='role-new', field_name='role', widget_attrs = {'data-widget-bootstrap': 'fill-field-bootstrap',})

dal.register(RoleAutocomplete, name='cast', choices=Role.objects.filter(cat='cast'))

dal.register(RoleAutocomplete, name='band', choices=Role.objects.filter(cat='band'))

dal.register(RoleAutocomplete, name='prod', choices=Role.objects.filter(cat='prod'))
