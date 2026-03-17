from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import (
    ResumeFresherExperience, ResumeHeader, ResumeSummary, 
    ResumeExperience, ResumeEducation, ResumeSkill, 
    ResumeAdditional, ResumeTemplate
)

# Required Imports for Analysis
import io
import pytesseract
from PIL import Image
from docx import Document
from pdfminer.high_level import extract_text
from django.contrib import messages

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

@login_required
def fresher_exp(request):
    """Step 0: Fresher vs Experience Selection"""
    if request.method == 'POST':
        experience_type = request.POST.get('type')
        ResumeFresherExperience.objects.update_or_create(
            user=request.user,
            defaults={'type': experience_type}
        )
        return redirect('edit_header')
    return render(request, 'resume/fresher_exp.html')

@login_required
def edit_header(request):
    """Step 1: Contact Header"""
    if request.method == 'POST':
        ResumeHeader.objects.update_or_create(
            user=request.user,
            defaults={
                'full_name': request.POST.get('full_name'),
                'profession': request.POST.get('profession'),
                'email': request.POST.get('email'),
                'phone': request.POST.get('phone'),
                'address': request.POST.get('address'),
                'linkedin': request.POST.get('linkedin'),
                'github': request.POST.get('github'),
                'website': request.POST.get('website')
            }
        )
        return redirect('edit_summary')
    
    # ✅ FIXED: Using filter().first() to avoid DoesNotExist error
    header = ResumeHeader.objects.filter(user=request.user).first()
    return render(request, 'resume/header.html', {'header': header})

@login_required
def edit_summary(request):
    """Step 2: Professional Summary"""
    if request.method == 'POST':
        summary_text = request.POST.get('summary')
        ResumeSummary.objects.update_or_create(
            user=request.user,
            defaults={'summary': summary_text}
        )
        return redirect('edit_experience')
    
    summary = ResumeSummary.objects.filter(user=request.user).first()
    return render(request, 'resume/summary.html', {'summary': summary})

@login_required
def edit_experience(request):
    """Step 3: Work History (Multiple Items)"""
    if request.method == 'POST':
        ResumeExperience.objects.filter(user=request.user).delete()
        total = int(request.POST.get('experience_count', 0))

        for i in range(total):
            job_title = request.POST.get(f'job_title_{i}')
            employer = request.POST.get(f'employer_{i}')
            currently_working = request.POST.get(f'currently_working_{i}') == 'on'

            if job_title and employer:
                e_month = request.POST.get(f'end_month_{i}')
                e_year = request.POST.get(f'end_year_{i}')
                
                ResumeExperience.objects.create(
                    user=request.user,
                    job_title=job_title,
                    employer=employer,
                    location=request.POST.get(f'location_{i}'),
                    start_month=request.POST.get(f'start_month_{i}'),
                    start_year=request.POST.get(f'start_year_{i}'),
                    end_month=None if currently_working else int(e_month) if e_month and e_month.isdigit() else None,
                    end_year=None if currently_working else int(e_year) if e_year and e_year.isdigit() else None,
                    currently_working=currently_working,
                    description=request.POST.get(f'description_{i}'),
                    skills=request.POST.get(f'skills_{i}')
                )
        return redirect('edit_education')

    experiences = ResumeExperience.objects.filter(user=request.user)
    return render(request, 'resume/experience.html', {'experiences': experiences})

@login_required
def edit_education(request):
    """Step 4: Education History"""
    if request.method == 'POST':
        ResumeEducation.objects.filter(user=request.user).delete()
        total = int(request.POST.get('education_count', 0))

        for i in range(total):
            inst = request.POST.get(f'institute_name_{i}')
            deg = request.POST.get(f'degree_{i}')
            if inst and deg:
                ResumeEducation.objects.create(
                    user=request.user,
                    institute_name=inst,
                    institute_location=request.POST.get(f'institute_location_{i}'),
                    degree=deg,
                    field_of_study=request.POST.get(f'field_of_study_{i}'),
                    start_year=int(request.POST.get(f'start_year_{i}', 0)),
                    end_year=int(request.POST.get(f'end_year_{i}', 0)),
                )
        return redirect('edit_skills')

    educations = ResumeEducation.objects.filter(user=request.user)
    return render(request, 'resume/education.html', {'educations': educations})

@login_required
def edit_skills(request):
    """Step 5: Skills"""
    if request.method == 'POST':
        ResumeSkill.objects.filter(user=request.user).delete()
        total = int(request.POST.get('skill_count', 0))
        for i in range(total):
            name = request.POST.get(f'skill_name_{i}')
            if name:
                ResumeSkill.objects.create(user=request.user, skill_name=name.strip())
        return redirect('edit_additional')

    skills = ResumeSkill.objects.filter(user=request.user)
    return render(request, 'resume/skills.html', {'skills': skills})

@login_required
def edit_additional(request):
    """Step 6: Languages/Certifications"""
    if request.method == "POST":
        ResumeAdditional.objects.filter(user=request.user).delete()
        count = int(request.POST.get("additional_count", 0))
        for i in range(count):
            title = request.POST.get(f"additional_title_{i}")
            if title:
                ResumeAdditional.objects.create(
                    user=request.user,
                    additional_title=title,
                    additional_desc=request.POST.get(f"additional_desc_{i}")
                )
        return redirect("select_template")

    # ✅ FIXED: Changed filter(request.user) to filter(user=request.user)
    additionals = ResumeAdditional.objects.filter(user=request.user)
    return render(request, "resume/additional.html", {"additionals": additionals})

@login_required
def select_template(request):
    """Step 7: Design Selection"""
    if request.method == "POST":
        selected = request.POST.get("template")
        if selected:
            ResumeTemplate.objects.update_or_create(
                user=request.user,
                defaults={"template_name": selected}
            )
            return redirect("resume_preview")
    return render(request, "resume/select_template.html")

@login_required
def resume_preview(request):
    """Step 8: Final Preview Render"""
    # Gathering data
    context = {
        "header": ResumeHeader.objects.filter(user=request.user).first(),
        "summary": ResumeSummary.objects.filter(user=request.user).first(),
        "experiences": ResumeExperience.objects.filter(user=request.user),
        "educations": ResumeEducation.objects.filter(user=request.user),
        "skills": ResumeSkill.objects.filter(user=request.user),
        "additionals": ResumeAdditional.objects.filter(user=request.user),
        "template": ResumeTemplate.objects.filter(user=request.user).first(),
    }

    # Template file mapping
    # Fallback to template1 if not explicitly found in the requested template name
    selected_name = context.get('template').template_name if context.get('template') else "template1"
    
    # We dynamically construct the template path to support all 20 templates
    template_path = f"resume/templates/{selected_name}.html"
    
    from django.template.loader import render_to_string
    from django.http import HttpResponse

    try:
        # Render the template to string
        html_content = render_to_string(template_path, context, request)
    except Exception as e:
        # Fallback if template doesn't exist
        html_content = render_to_string("resume/templates/template1.html", context, request)

    # Inject the floating toolbar before the closing </body> tag
    toolbar_html = render_to_string("resume/components/floating_toolbar.html", {}, request)
    if '</body>' in html_content:
        html_content = html_content.replace('</body>', f'{toolbar_html}</body>')
    else:
        html_content += toolbar_html

    return HttpResponse(html_content)

# --- UTILITY: File Parsing ---
def get_raw_text(file):
    extension = file.name.split('.')[-1].lower()
    if extension == 'pdf':
        return extract_text(io.BytesIO(file.read()))
    elif extension in ['docx', 'doc']:
        doc = Document(file)
        return '\n'.join([p.text for p in doc.paragraphs])
    elif extension in ['jpg', 'jpeg', 'png']:
        return pytesseract.image_to_string(Image.open(file))
    return ""

@login_required
def upload_resume(request):
    if request.method == 'POST' and request.FILES.get('resume'):
        resume_file = request.FILES['resume']
        raw_text = get_raw_text(resume_file)
        if raw_text:
            messages.success(request, "Analysis complete! Pick your template.")
            return redirect('select_template')
        else:
            messages.error(request, "Format not supported.")
    return render(request, 'resume/upload_resume.html')