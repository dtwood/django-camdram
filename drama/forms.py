from haystack.forms import SearchForm
import hashlib
import datetime
import dal
import dal.widgets
import dal.forms
from django import forms
from django.forms.models import inlineformset_factory
from drama import models
from registration.forms import RegistrationForm
from django.contrib.auth.models import User


class CamdramSearchForm(SearchForm):
    q = forms.CharField(required=False, widget=forms.widgets.TextInput(
        attrs={"class": "searchfield", "placeholder": "Search for a person, venue, show or society...", 'id': 'searchfield', 'autocomplete': 'off'}))


class FormsetsForm(forms.ModelForm):
    formsets = {}
    context = {}

    def __init__(self, *args, initial=None, **kwargs):
        super(FormsetsForm, self).__init__(initial=initial, *args, **kwargs)
        self.bound_formsets = []
        self.context = {}
        for name, formset in self.formsets.items():
            bound_f = formset(*args, **kwargs)
            self.context[name] = bound_f

    def clean(self, *args, **kwargs):
        cleaned_data = super(FormsetsForm, self).clean()
        for k,x in self.context.items():
            if not x.is_valid():
                raise forms.ValidationError(
                    "Error in editing %(model)s", params={'model': str(x.form._meta.model)})
            cleaned_data[k] = x
        return cleaned_data

    def save(self, *args, **kwargs):
        result = super(FormsetsForm, self).save(*args, **kwargs)
        for _,formset in self.context.items():
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

    def __init__(self, *args, parent=None, parent_name=None, **kwargs):
        self.parent = parent
        self.parent_name = parent_name
        super(ChildForm, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        super(ChildForm,self).save(*args, **kwargs)


    def clean(self):
        cleaned_data = super(ChildForm, self).clean()
        if self.parent is not None:
            cleaned_data[self.parent_name] = self.parent
            self._meta.fields += [self.parent_name]
        return cleaned_data


class PerformanceForm(dal.forms.FutureModelForm):

    class Meta:
        model = models.Performance
        fields = ['start_date','end_date','time','venue']
        widgets = {
            'start_date': forms.DateInput(attrs={'class':'date'}),
            'end_date': forms.DateInput(attrs={'class':'date'}),
            }

PerformanceInline = inlineformset_factory(
    models.Show, models.Performance, PerformanceForm, extra=1)

class ShowForm(FormsetsForm, dal.forms.FutureModelForm):
    error_css_class = 'error'
    required_css_class = 'required'
    formsets = {'performance_formset': PerformanceInline}

    class Meta:
        model = models.Show
        fields = ['name','desc','book','prices','author','societies','image', 'facebook_id', 'twitter_id']

    def clean(self, *args, **kwargs):
        cleaned_data = super(ShowForm, self).clean()
        year = None
        for form in cleaned_data['performance_formset']:
            if 'start_date' in form.cleaned_data.keys():
                new_year = form.cleaned_data['start_date'].year
                if (not year) or (new_year < year):
                    year = new_year
        cleaned_data['year'] = year
        return cleaned_data


class SocietyForm(FormsetsForm):
    error_css_class = 'error'
    required_css_class = 'required'
    formsets = {}

    class Meta:
        model = models.Society
        fields = ['name','shortname','desc','image', 'facebook_id', 'twitter_id']


class PersonForm(FormsetsForm):
    error_css_class = 'error'
    required_css_class = 'required'
    formsets = {}

    class Meta:
        model = models.Person
        fields = ['name','desc']


class VenueForm(FormsetsForm):
    error_css_class = 'error'
    required_css_class = 'required'
    formsets = {}

    class Meta:
        model = models.Venue
        fields = ['name','desc','address','lat','lng', 'facebook_id', 'twitter_id']

        
class RoleForm(FormsetsForm):
    error_css_class = 'error'
    required_css_class = 'required'
    formsets = {}

    class Meta:
        model = models.Role
        fields = ['name','desc','cat']


class AuditionInstanceForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'class':'date'}))
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
            cleaned_data['end_datetime'] = datetime.datetime.combine(
                cleaned_data['date'], cleaned_data['end_time'])
        except KeyError:
            pass
        return cleaned_data

    
    class Meta:
        model = models.AuditionInstance
        fields = ['end_datetime','start_time','location']
        

        
AuditionInline = inlineformset_factory(
    models.Audition, models.AuditionInstance, AuditionInstanceForm, extra=1)


class AuditionForm(ChildForm):
    error_css_class = 'error'
    required_css_class = 'required'
    formsets = {'audition_formset':AuditionInline}
    
    class Meta:
        model = models.Audition
        fields = ['desc','contact']

        
class TechieAdRoleForm(dal.forms.FutureModelForm):

    class Meta:
        model = models.TechieAdRole
        fields = ['name','desc','role']

        
TechieAdInline = inlineformset_factory(
    models.TechieAd, models.TechieAdRole, TechieAdRoleForm, extra=1)


class DeadlineForm(forms.ModelForm):
    date = forms.DateField(label="Deadline date", widget=forms.DateInput(attrs={'class':'date'}))
    time = forms.TimeField(label="Deadline time")

    def __init__(self, *args, instance = None, initial=None, **kwargs):
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
            cleaned_data['deadline'] = datetime.datetime.combine(
                cleaned_data['date'], cleaned_data['time'])
        except KeyError:
            pass
        return cleaned_data
    

class TechieAdForm(DeadlineForm, ChildForm):
    error_css_class = 'error'
    required_css_class = 'required'
    formsets = {'techiead_formset':TechieAdInline}
    

    class Meta:
        model = models.TechieAd
        fields = ['desc','contact','deadline']

class ApplicationForm(DeadlineForm, FormsetsForm, dal.forms.FutureModelForm):
    error_css_class = 'error'
    required_css_class = 'required'
    formsets = {}
    
    class Meta:
        model = models.Application
        fields = ['name','desc','contact','deadline']


ShowApplicationFormset = inlineformset_factory(models.Show, models.ShowApplication, ApplicationForm)
VenueApplicationFormset = inlineformset_factory(models.Venue, models.VenueApplication, ApplicationForm)
SocietyApplicationFormset = inlineformset_factory(models.Society, models.SocietyApplication, ApplicationForm)

class CastForm(forms.Form):
    role = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Role'}))
    person = forms.ModelChoiceField(models.Person.objects.all(),
            widget=dal.widgets.Select('PersonAutocomplete',
                    attrs={'placeholder':'Person'}))

class BandForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Custom Name'}))
    role = forms.ModelChoiceField(models.Role.objects.filter(cat='band'),
        widget=dal.widgets.Select('band',
            attrs={'placeholder':'Role'}))
    person = forms.ModelChoiceField(models.Person.objects.all(),
            widget=dal.widgets.Select('PersonAutocomplete',
                    attrs={'placeholder':'Person'}))

class ProdForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Custom Name'}))
    role = forms.ModelChoiceField(models.Role.objects.filter(cat='prod'),
        widget=dal.widgets.Select('prod',
            attrs={'placeholder':'Role'},))
    person = forms.ModelChoiceField(models.Person.objects.all(),
            widget=dal.widgets.Select('PersonAutocomplete',
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

class DiaryJumpForm(forms.Form):
    term = forms.ChoiceField(choices=models.TermDate.TERM_CHOICES)
    year = forms.ChoiceField(choices=models.TermDate.YEAR_CHOICES)

class EmailForm(forms.Form):
    '''
    For previewing/sending EmailList messages.
    '''
    address = forms.EmailField()
    subject = forms.CharField(max_length=256)
    header = forms.CharField(widget=forms.Textarea())


class EmailListForm(forms.ModelForm):
    error_css_class = 'error'
    required_css_class = 'required'

    class Meta:
        model = models.EmailList
        fields = ['name', 'desc', 'default_address', 'from_addr', 'default_subject', 'default_header', 'html_template','plaintext_template', 'date_format']

