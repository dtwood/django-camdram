from django.core.urlresolvers import reverse

def navitems_processor(request):
    return {'navitems_default':
            (('home', {'text': 'Home', 'path': reverse('home')}),
            ('diary', {'text': 'Diary', 'path': reverse('diary')}),
            ('vacancies', {'text': 'Vacancies', 'path': reverse('auditions')}),
            ('societies', {'text': 'Societies', 'path': reverse('societies')}),
            ('venues', {'text': 'Venues', 'path': reverse('venues')}),
            )}
