from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True)

class Vacancy(models.Model):
    url = models.URLField(verbose_name='Vacancy URL')
    date_published = models.DateField(blank=True, null=True)
    company = models.CharField(max_length=40)
    position = models.CharField(max_length=40)
    description = models.TextField()
    requirements = models.TextField()
    recruiter_name = models.CharField(max_length=30, blank=True, null=True)
    recruiter_position = models.CharField(max_length=30, blank=True, null=True)
    recruiter_email = models.EmailField(blank=True, null=True, default='')
    user = models.ForeignKey(User, on_delete=models.CASCADE)


STATUS_CHOICES = [
    ('No reply', 'No reply'),
    ('Call scheduled', 'Call scheduled'),
    ('Declined', 'Declined')
]

def user_directory_path(instance, filename):
    # file will be uploaded to BASE_DIR/vacancy_<id>/<filename>
    return 'resume_files/vacancy_{0}/{1}'.format(instance.vacancy.id, filename)

class JobApplication(models.Model):
    date_submitted = models.DateField()
    resume = models.FileField(upload_to=user_directory_path)
    cover_letter = models.FileField(upload_to=user_directory_path, blank=True, null=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, blank=False, default='No reply')
    vacancy = models.ForeignKey(Vacancy, related_name='applications', on_delete=models.CASCADE)
