from haystack.forms import SearchForm
from django import forms

class CamdramSearchForm(SearchForm):
    q = forms.CharField(required=False, widget=forms.widgets.TextInput(attrs={"class":"searchfield", "placeholder":"Search for a person, venue, show or society...", 'id':'searchfield', 'autocomplete':'off'}))
    class Media:
        js = ('js/jquery-2.1.0.js','js/jquery-ui-1.10.4.custom.js','js/autocomplete.js',)
        css = {'all':('css/font-awesome.css','css/main.css','css/ui-lightness/jquery-ui-1.10.4.custom.css'),}
