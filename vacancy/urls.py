from django.urls import path
from django.conf.urls import include
from django.contrib.auth.views import LoginView
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView

from vacancy.views import VacancyIndexView, VacancyDetailsView, VacancyCreateView, ApplicationCreateView, OpenFileView, VacancyDeleteView, AppDeleteView, PasswordsChangeView

from . import views

urlpatterns = [
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('favicon.ico'))),
    path('accounts/login/', LoginView.as_view(redirect_authenticated_user=True), name='login'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', views.register, name='register'),
    path('accounts/change-password', PasswordsChangeView.as_view(), name='change_password'),
    path('<int:pk>/delete/', VacancyDeleteView.as_view(), name='vacancy_delete'),
    path('<int:pk>/open-file/', OpenFileView.as_view(), name='open_file'),
    path('<int:pk>/delete-application/', AppDeleteView.as_view(), name='application_delete'),
    path('index/', VacancyIndexView.as_view(), name='vacancy_index'),
    path('<int:pk>/', VacancyDetailsView.as_view(), name='vacancy_detail'),
    path('add/', VacancyCreateView.as_view(), name='vacancy_create'),
    path('application/<int:pk>/', ApplicationCreateView.as_view(), name='job_application'),
]