from django.core.urlresolvers import reverse
from drama.forms import CamdramSearchForm

def navitems_processor(request):
    return {'navitems_default':
            (('home', {'text': 'Home', 'path': reverse('home')}),
            ('diary', {'text': 'Diary', 'path': reverse('diary')}),
            ('vacancies', {'text': 'Vacancies', 'path': reverse('auditions')}),
            ('societies', {'text': 'Societies', 'path': reverse('list', kwargs={'model_name':'societies'})}),
            ('venues', {'text': 'Venues', 'path': reverse('list', kwargs={'model_name':'venues'})}),
            )}

def searchform(request):
    return {'search_form': CamdramSearchForm()}
