from haystack.forms import SearchForm
from django import forms
from django.forms.models import inlineformset_factory
from drama.models import *


class CamdramSearchForm(SearchForm):
    q = forms.CharField(required=False, widget=forms.widgets.TextInput(attrs={"class":"searchfield", "placeholder":"Search for a person, venue, show or society...", 'id':'searchfield', 'autocomplete':'off'}))
    class Media:
        js = ('js/jquery-2.1.0.js','js/jquery-ui-1.10.4.custom.js','js/autocomplete.js',)
        css = {'all':('css/font-awesome.css','css/main.css','css/ui-lightness/jquery-ui-1.10.4.custom.css'),}

class FormsetsForm(forms.ModelForm):
    formsets = []
    bound_formsets = []
    context = {}
    def bind_formsets(self, *args, **kwargs):
        self.bound_formsets = []
        self.context = {}
        for name,formset in self.formsets.items():
            bound_f = formset(*args, **kwargs)
            self.bound_formsets.append(bound_f)
            self.context[name] = bound_f
    def get_context(self):
        return self.context
    def clean(self, *args, **kwargs):
        cleaned_data = super(FormsetsForm, self).clean()
        for x in self.bound_formsets:
            if not x.is_valid():
                raise forms.ValidationError("Error in editing %(model)s",params={'model':x.model.get_cname()})
        return cleaned_data
    
    def save(self, *args, **kwargs):
        result = super(FormsetsForm,self).save(*args,**kwargs)
        for formset in self.bound_formsets:
            formset_class = formset.__class__
            new_formset = formset_class(data=formset.data, instance=result)
            new_formset.is_valid()
            new_formset.save()
        return result
    
PerformanceInline = inlineformset_factory(Show, Performance, extra=1)
RoleInline = inlineformset_factory(Show, RoleInstance)

class ShowForm(FormsetsForm):
    error_css_class = 'error'
    required_css_class = 'required'
    formsets = {'performance_formset':PerformanceInline}
    class Meta:
        model = Show

class SocietyForm(FormsetsForm):
    error_css_class = 'error'
    required_css_class = 'required'
    formsets = {}
    class Meta:
        model = Society

class PersonForm(FormsetsForm):
    error_css_class = 'error'
    required_css_class = 'required'
    formsets = {}
    class Meta:
        model = Person

class VenueForm(FormsetsForm):
    error_css_class = 'error'
    required_css_class = 'required'
    formsets = {}
    class Meta:
        model = Venue
