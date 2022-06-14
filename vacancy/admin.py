from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

from vacancy.models import Vacancy
from vacancy.models import JobApplication

admin.site.register(Vacancy)
admin.site.register(JobApplication)
admin.site.register(User, UserAdmin)
