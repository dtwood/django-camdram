from haystack.forms import SearchForm
import hashlib
import datetime
import autocomplete_light
autocomplete_light.autodiscover()
from django import forms
from django.forms.models import inlineformset_factory
from drama.models import *
from registration.forms import RegistrationForm
from django.contrib.auth.models import User


class CamdramSearchForm(SearchForm):
    q = forms.CharField(required=False, widget=forms.widgets.TextInput(
        attrs={"class": "searchfield", "placeholder": "Search for a person, venue, show or society...", 'id': 'searchfield', 'autocomplete': 'off'}))


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


class ChildForm(FormsetsForm):
    '''
    For creating and editing objects with a parent object
    field, which should not be editable.
    '''
    parent = None
    parent_name = None

    def __init__(self, parent=None, parent_name=None, *args, **kwargs):
        self.parent = parent
        self.parent_name = parent_name
        if self._meta.exclude is not None:
            if self.parent_name is not None and self.parent_name not in self._meta.exclude:
                self._meta.exclude = (self.parent_name,) + self._meta.exclude
        else:
            if self.parent_name is not None:
                self._meta.exclude = (self.parent_name,)
        super(ChildForm, self).__init__(*args, **kwargs)
        if self.parent_name is not None:
            del self.fields[self.parent_name]

    def save(self, *args, **kwargs):
        super(ChildForm,self).save(*args, **kwargs)


    def clean(self):
        cleaned_data = super(ChildForm, self).clean()
        if self.parent is not None:
            self._meta.exclude = tuple(x for x in self._meta.exclude if x != self.parent_name)
        if self.parent is not None:
            cleaned_data[self.parent_name] = self.parent
        return cleaned_data


class PerformanceForm(autocomplete_light.ModelForm):

    class Meta:
        model = Performance

PerformanceInline = inlineformset_factory(
    Show, Performance, PerformanceForm, extra=1)

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

        
class RoleForm(FormsetsForm):
    error_css_class = 'error'
    required_css_class = 'required'
    formsets = {}

    class Meta:
        model = Role


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


class AuditionForm(ChildForm):
    error_css_class = 'error'
    required_css_class = 'required'
    formsets = {'audition_formset':AuditionInline}
    
    class Meta:
        model = Audition

        
class TechieAdRoleForm(autocomplete_light.ModelForm):

    class Meta:
        model = TechieAdRole

        
TechieAdInline = inlineformset_factory(
    TechieAd, TechieAdRole, TechieAdRoleForm, extra=5)
class DeadlineForm(forms.ModelForm):
    date = forms.DateField(label="Deadline date")
    time = forms.TimeField(label="Deadline time")

    def __init__(self, instance = None, initial=None, *args, **kwargs):
        if initial is None:
            initial = {}
        if instance is not None:
            temp = instance.deadline
            initial.update({'date': temp.date(),
                            'time': temp.time(),
                            })
        super(DeadlineForm, self).__init__(initial=initial, instance=instance, *args, **kwargs)

        
    def clean(self):
        cleaned_data = super(DeadlineForm, self).clean()
        if 'deadline' in self._errors:
            del self._errors['deadline']
        try:
            cleaned_data['deadline'] = datetime.combine(
                cleaned_data['date'], cleaned_data['time'])
        except KeyError:
            pass
        return cleaned_data
    

class TechieAdForm(DeadlineForm, ChildForm):
    error_css_class = 'error'
    required_css_class = 'required'
    formsets = {'techiead_formset':TechieAdInline}
    

    class Meta:
        model = TechieAd


class ApplicationForm(DeadlineForm, FormsetsForm, autocomplete_light.ModelForm):
    error_css_class = 'error'
    required_css_class = 'required'
    formsets = {}
    
    class Meta:
        model = Application


ShowApplicationFormset = inlineformset_factory(Show, ShowApplication, ApplicationForm)
VenueApplicationFormset = inlineformset_factory(Venue, VenueApplication, ApplicationForm)
SocietyApplicationFormset = inlineformset_factory(Society, SocietyApplication, ApplicationForm)

class CastForm(forms.Form):
    role = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Role'}))
    person = forms.ModelChoiceField(Person.objects.all(),
            widget=autocomplete_light.ChoiceWidget('PersonAutocomplete',
                    attrs={'placeholder':'Person'}))

class BandForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Custom Name'}))
    role = forms.ModelChoiceField(Role.objects.filter(cat='band'),
        widget=autocomplete_light.ChoiceWidget('band',
            attrs={'placeholder':'Role'},
            widget_attrs = {'data-widget-bootstrap': 'fill-field-bootstrap',}))
    person = forms.ModelChoiceField(Person.objects.all(),
            widget=autocomplete_light.ChoiceWidget('PersonAutocomplete',
                    attrs={'placeholder':'Person'}))

class ProdForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Custom Name'}))
    role = forms.ModelChoiceField(Role.objects.filter(cat='prod'),
        widget=autocomplete_light.ChoiceWidget('prod',
            attrs={'placeholder':'Role'},
            widget_attrs = {'data-widget-bootstrap': 'fill-field-bootstrap',}))
    person = forms.ModelChoiceField(Person.objects.all(),
            widget=autocomplete_light.ChoiceWidget('PersonAutocomplete',
                    attrs={'placeholder':'Person'}))


class EmailRegistrationForm(RegistrationForm):
    def __init__(self, *args, **kwargs):
        super(EmailRegistrationForm, self).__init__(*args, **kwargs)
        del self.fields['username']

    def clean_email(self):
        """
        Validate that the email is not already in use.
        
        """
        existing = User.objects.filter(username__iexact=hashlib.md5(self.cleaned_data['email'].encode('utf-8')).hexdigest())[0:30]
        if existing.exists():
            raise forms.ValidationError(_("A user with that username already exists."))
        else:
            return self.cleaned_data['email']

class AdminForm(forms.Form):
    email = forms.EmailField()
