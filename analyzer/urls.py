from django import views
from django.urls import path
from django.conf import settings # ADDED: To access MEDIA/STATIC settings
from django.conf.urls.static import static # ADDED: To serve files in development
from .views_auth import *
from .views_resume import *
from .views import *
from .views_resume import ats_analyze

urlpatterns = [
    path('', dashboard, name='home'),
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    path('dashboard/', dashboard, name='dashboard'),
    path('resume/fresher_exp/', fresher_exp, name='fresher_exp'),
    
    # --- ADDED: Project 2 - Resume Upload Path ---
    # Reason: Required to handle the "Upgrade My Resume" redirection
    path('resume/upload_resume/', upload_resume, name='upload_resume'),
    # ✅ ADD THIS EXACT LINE:
    path('myaccounts/', my_accounts, name='my_accounts'),    
    path('resume/header/', edit_header, name='edit_header'),
    path('resume/summary/', edit_summary, name='edit_summary'),
    path("ai/generate-summary/", ai_generate_summary),
    path("ai/optimize-summary/", ai_optimize_summary),
    path('resume/experience/', edit_experience, name='edit_experience'),
    path('resume/education/', edit_education, name='edit_education'),
    path('resume/skills/', edit_skills, name='edit_skills'),
    path('resume/additional/', edit_additional, name='edit_additional'),
    path('resume/templates/', select_template, name='select_template'),
    path('resume/preview/', resume_preview, name='resume_preview'),
    path('resume/render_template/', render_resume_template, name='render_resume_template'),
    path('resume/ats-analyze/', ats_analyze, name='ats_analyze'),
]

# --- ADDED: Development Helpers ---
# Reason: Allows Django to serve uploaded resumes and profile photos while DEBUG=True
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)