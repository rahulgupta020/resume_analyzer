from django.db import models
from django.contrib.auth.models import User
from django.db import models

class ResumeFresherExperience(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='fresher_experience')
    type = models.CharField(max_length=50, choices=[('Fresher', 'Fresher'), ('Experienced', 'Experienced')])

class ResumeHeader(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='resume_header')
    full_name = models.CharField(max_length=100)
    profession = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255, blank=True)
    linkedin = models.URLField(blank=True)
    github = models.URLField(blank=True)
    website = models.URLField(blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)

class ResumeSummary(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='resume_summary')
    summary = models.TextField()

class ResumeExperience(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resume_experiences')
    job_title = models.CharField(max_length=100)
    employer = models.CharField(max_length=100)
    location = models.CharField(max_length=255, blank=True)
    start_month = models.IntegerField(null=True, blank=True)
    start_year = models.IntegerField(null=True, blank=True)
    end_month = models.IntegerField(null=True, blank=True)
    end_year = models.IntegerField(null=True, blank=True)
    currently_working = models.BooleanField(default=False)
    description = models.TextField()
    skills = models.CharField(max_length=255, blank=True)

class ResumeEducation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resume_education')
    institute_name = models.CharField(max_length=150)
    institute_location = models.CharField(max_length=255, blank=True)
    degree = models.CharField(max_length=100)
    field_of_study = models.CharField(max_length=100)
    start_year = models.IntegerField(null=True, blank=True)
    end_year = models.IntegerField(null=True, blank=True)

class ResumeSkill(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resume_skills')
    skill_name = models.CharField(max_length=50)

class ResumeAdditional(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resume_additional')
    additional_title = models.CharField(max_length=100)
    additional_desc = models.TextField(blank=True)

class ResumeTemplate(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='resume_template')
    template_name = models.CharField(max_length=50)
