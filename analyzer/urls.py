from django.urls import path
from .views_auth import *
from .views_resume import *
from .views import *

urlpatterns = [
    path('', dashboard, name='home'),
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    path('dashboard/', dashboard, name='dashboard'),
    path('resume/fresher_exp/', fresher_exp, name='fresher_exp'),
    path('resume/header/', edit_header, name='edit_header'),
    path('resume/summary/', edit_summary, name='edit_summary'),
    path('resume/experience/', edit_experience, name='edit_experience'),
    path('resume/education/', edit_education, name='edit_education'),
    path('resume/skills/', edit_skills, name='edit_skills'),
    path('resume/additional/', edit_additional, name='edit_additional'),
    path('resume/templates/', select_template, name='select_template'),
    path('resume/preview/', resume_preview, name='resume_preview'),
]
