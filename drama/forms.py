from haystack.forms import SearchForm
from django import forms

class CamdramSearchForm(SearchForm):
    q = forms.CharField(required=False, widget=forms.widgets.TextInput(attrs={"class":"searchfield", "placeholder":"Search for a person, venue, show or society...", 'id':'searchfield', 'autocomplete':'off'}))
