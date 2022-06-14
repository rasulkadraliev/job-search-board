import os
import boto3

from django.core.files.storage import default_storage
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, DetailView, View, CreateView

from jobSearch.settings import AWS_STORAGE_BUCKET_NAME as s3_bucket_name
from vacancy.models import Vacancy, JobApplication
from vacancy.forms import VacancyForm, JobApplicationForm, UserRegisterForm

# Returns template with a list of vacancies saved by user
class VacancyIndexView(LoginRequiredMixin, TemplateView):
    template_name = 'vacancy_index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vacancies'] = Vacancy.objects.filter(user=self.request.user)
        return context

# Returns template wth details of a saved vacancy, i.e. url, company name,
# vacant position, etc.
class VacancyDetailsView(LoginRequiredMixin, DetailView):
    model = Vacancy
    template_name = 'vacancy_detail.html'

    # Get request is not be allowed as user id data should be submitted
    # hence it's redirecting to the index page
    def get(self, request, **kwargs):
        return redirect('vacancy_index')

    def post(self, request, **kwargs):
        context = {}
        context['vacancy'] = Vacancy.objects.get(pk=self.kwargs['pk'])
        return render(request, template_name='vacancy_detail.html', context=context)

# Creates vacancy object with all details in DB
class VacancyCreateView(LoginRequiredMixin, CreateView):
    form_class = VacancyForm
    template_name = 'vacancy_create.html'

    # method picks current user's username and adds to a form
    # at initial load. This is needed to assign a user to a
    # vacancy being created in DB
    def get_initial(self):
        return {'user': self.request.user}

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            form.save()
            # Checks if tag 'save' is in the request, meaning user clicked
            # button 'Save & Exit' and redirects to index page.
            if 'save' in request.POST:
                return redirect('vacancy_index')

        # Otherwise, user clicked button 'Save & Add new' and hence method
        # returns to vacancy creation template
        return redirect('vacancy_create')

# Creates 'application' object in Job Application table when user clicks
# 'Apply' button in Vacancy details
class ApplicationCreateView(LoginRequiredMixin, CreateView):
    form_class = JobApplicationForm
    template_name = 'job_application.html'
    success_url = reverse_lazy('vacancy_index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vacancy'] = Vacancy.objects.get(pk=self.kwargs['pk'])
        return context

    def get_initial(self):
        return {'vacancy': self.kwargs['pk']}

# Serves to view in browser a resume or a cover letter file
# saved along with job application
class OpenFileView(LoginRequiredMixin, View):

    def get(self, request, pk):
        file_to_open = JobApplication.objects.get(vacancy=pk)
        if "cover_letter" in self.request.GET:
            file_path = file_to_open.cover_letter.name
            return redirect(default_storage.url(file_path))
        else:
            file_path = file_to_open.resume.name
            return redirect(default_storage.url(file_path))

# Serves to delete 'vacancy' object from DB
class VacancyDeleteView(LoginRequiredMixin, View):

    def get(self):
        return redirect('vacancy_index')

    def post(self, request, pk):
        vacancy = Vacancy.objects.get(pk=pk)
        #Checks if requested 'vacancy' object exists
        # If not, returns to index page
        if not vacancy:
            return redirect('vacancy_index')
        # Checks if requested 'vacancy' object had 'application'
        # object, linked to the vacancy
        try:
            application = JobApplication.objects.get(vacancy=pk)
        except JobApplication.DoesNotExist:
            application = None
        # If application object exists - deletes vacancy and with files - resume
        # and cover letter (if any) too
        if application:
            vacancy.delete()
            s3 = boto3.resource('s3')
            bucket = s3.Bucket(s3_bucket_name)
            bucket.object_versions.filter(
                Prefix=os.path.join('resume_files', 'vacancy_{0}'.format(application.vacancy.id))).delete()
        else:
            vacancy.delete()
        return redirect('vacancy_index')

# Deletes job application object only ('vacancy' object stays) when
# user clicks 'Delete application' button on 'Vacancy details' template
class AppDeleteView(LoginRequiredMixin, View):

    def post(self, request, pk):
        application = JobApplication.objects.get(vacancy=pk)
        application.delete()
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(s3_bucket_name)
        bucket.object_versions.filter(
            Prefix=os.path.join('resume_files', 'vacancy_{0}'.format(application.vacancy.id))).delete()
        return redirect ('vacancy_index')

# This view is done with function, not class for a change :) and it
# returns user registration template
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            first_name = form.cleaned_data.get('first_name')
            messages.success(request, f'Congratulation! Account has been created for {first_name}.')
            login(request, user)
            return render(request, 'registration/login.html', {'form': AuthenticationForm()})
    else:
        form = UserRegisterForm()
    return render(request, 'registration/register.html', {'form': form})

# Returns password change template
class PasswordsChangeView(PasswordChangeView):
    template_name = 'registration/change-password.html'
    success_url = reverse_lazy('vacancy_index')

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            messages.success(request, f'Your password was successfully changed!')
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

