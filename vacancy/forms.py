from django import forms
from django.forms.widgets import NumberInput
from django.contrib.auth.forms import UserCreationForm
from .models import Vacancy, JobApplication, User


class VacancyForm(forms.ModelForm):
    date_published = forms.DateField(required=False, widget=NumberInput(attrs={'type': 'date'}))

    def __init__(self, *args, **kwargs):
        super(VacancyForm, self).__init__(*args, **kwargs)
        self.fields['description'].widget.attrs.update({'id': 'description'}) # this is for html template to adjust the style of those fields
        self.fields['requirements'].widget.attrs.update({'id': 'requirements'}) # this is for html template to adjust the style of those fields

    class Meta:
        model = Vacancy
        fields = '__all__'
        # To hide user id from vacancy form
        widgets = {'user': forms.HiddenInput()}

class JobApplicationForm(forms.ModelForm):
    date_submitted = forms.DateField(widget=NumberInput(attrs={'type': 'date'}))

    def __init__(self, *args, **kwargs):
        super(JobApplicationForm, self).__init__(*args, **kwargs)
        self.fields['status'].widget.attrs.update({'id':'status'})
        self.fields['date_submitted'].widget.attrs.update({'id': 'date_submitted'})

    class Meta:
        model = JobApplication
        fields = '__all__'
        # To hide vacancy id from vacancy form
        widgets = {'vacancy': forms.HiddenInput()}

class UserRegisterForm(UserCreationForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
