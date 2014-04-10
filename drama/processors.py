from django.core.urlresolvers import reverse
from drama.forms import CamdramSearchForm
from drama.models import Society, Venue, Role


def navitems_processor(request):
    return {'navitems_default':
            (('home', {'text': 'Home', 'path': reverse('home')}),
             ('diary', {'text': 'Diary', 'path': reverse('diary')}),
             ('vacancies', {
              'text': 'Vacancies', 'path': reverse('auditions')}),
             ('societies', {'text': 'Societies', 'path': Society.get_list_url()}),
             ('venues', {'text': 'Venues', 'path': Venue.get_list_url()}),
             ('roles', {'text': 'Roles', 'path': Role.get_list_url()}),
             )}


def searchform(request):
    return {'search_form': CamdramSearchForm()}
