from django import forms

class ResponseForm(forms.Form):
    body = forms.CharField(widget=forms.Textarea)
