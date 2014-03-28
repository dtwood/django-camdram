from haystack.forms import SearchForm
import datetime
import autocomplete_light
autocomplete_light.autodiscover()
from django import forms
from django.forms.models import inlineformset_factory
from drama.models import *


class CamdramSearchForm(SearchForm):
    q = forms.CharField(required=False, widget=forms.widgets.TextInput(
        attrs={"class": "searchfield", "placeholder": "Search for a person, venue, show or society...", 'id': 'searchfield', 'autocomplete': 'off'}))

    class Media:
        js = ('js/jquery-2.1.0.js', 'js/jquery-ui-1.10.4.custom.js',
              'js/autocomplete.js',)
        css = {'all': ('css/font-awesome.css', 'css/main.css',
                       'css/ui-lightness/jquery-ui-1.10.4.custom.css'), }


class FormsetsForm(forms.ModelForm):
    formsets = []
    bound_formsets = []
    context = {}

    def bind_formsets(self, *args, **kwargs):
        self.bound_formsets = []
        self.context = {}
        for name, formset in self.formsets.items():
            bound_f = formset(*args, **kwargs)
            self.bound_formsets.append(bound_f)
            self.context[name] = bound_f

    def get_context(self):
        return self.context

    def clean(self, *args, **kwargs):
        cleaned_data = super(FormsetsForm, self).clean()
        for x in self.bound_formsets:
            if not x.is_valid():
                raise forms.ValidationError(
                    "Error in editing %(model)s", params={'model': x.model.get_cname()})
        return cleaned_data

    def save(self, *args, **kwargs):
        result = super(FormsetsForm, self).save(*args, **kwargs)
        for formset in self.bound_formsets:
            formset_class = formset.__class__
            new_formset = formset_class(data=formset.data, instance=result)
            new_formset.is_valid()
            new_formset.save()
        return result


class PerformanceForm(autocomplete_light.ModelForm):

    class Meta:
        model = Performance

class AuditionInstanceForm(forms.ModelForm):
    date = forms.DateField()
    end_time = forms.TimeField()

    def __init__(self, instance = None, initial=None, *args, **kwargs):
        if initial is None:
            initial = {}
        if instance is not None:
            temp = instance.end_datetime
            initial.update({'date': temp.date(),
                            'end_time': temp.time(),
                            })
        super(AuditionInstanceForm, self).__init__(initial=initial, instance=instance, *args, **kwargs)

        
    def clean(self):
        cleaned_data = super(AuditionInstanceForm, self).clean()
        if 'end_datetime' in self._errors:
            del self._errors['end_datetime']
        try:
            cleaned_data['end_datetime'] = datetime.combine(
                cleaned_data['date'], cleaned_data['end_time'])
        except KeyError:
            pass
        return cleaned_data

    
    class Meta:
        model = AuditionInstance

AuditionInline = inlineformset_factory(
    Audition, AuditionInstance, AuditionInstanceForm, extra=1)

PerformanceInline = inlineformset_factory(
    Show, Performance, PerformanceForm, extra=1)

RoleInline = inlineformset_factory(Show, RoleInstance)


class ShowForm(FormsetsForm, autocomplete_light.ModelForm):
    error_css_class = 'error'
    required_css_class = 'required'
    formsets = {'performance_formset': PerformanceInline}

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


class AuditionForm(FormsetsForm):
    error_css_class = 'error'
    required_css_class = 'required'
    formsets = {'audition_formset':AuditionInline}
    this_show = None

    def __init__(self, show=None, *args, **kwargs):
        super(AuditionForm, self).__init__(*args, **kwargs)
        self.this_show = show

    def save(self, *args, **kwargs):
        if self.this_show is not None:
            self._meta.exclude = None
        super(AuditionForm,self).save(*args, **kwargs)


    def clean(self):
        if self.this_show is not None:
            self._meta.exclude = None
        cleaned_data = super(AuditionForm, self).clean()
        if self.this_show is not None:
            cleaned_data['show'] = self.this_show
        return cleaned_data

    class Meta:
        model = Audition
        exclude = ('show',)


class TechieAdForm(FormsetsForm):
    error_css_class = 'error'
    required_css_class = 'required'
    formsets = {}

    class Meta:
        model = TechieAd

        
class RoleForm(FormsetsForm):
    error_css_class = 'error'
    required_css_class = 'required'
    formsets = {}

    class Meta:
        model = Role
