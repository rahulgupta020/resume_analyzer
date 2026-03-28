import time

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.clickjacking import xframe_options_exempt
from .models import (
    ResumeFresherExperience, ResumeHeader, ResumeSummary, 
    ResumeExperience, ResumeEducation, ResumeSkill, 
    ResumeAdditional, ResumeTemplate
)
from .ai_resume_parser import parse_resume_with_ai

# Required Imports for Analysis
import io
import pytesseract
from PIL import Image
from docx import Document
from pdfminer.high_level import extract_text
from django.contrib import messages

import ollama
import json
from django.http import JsonResponse
import json
from django.http import JsonResponse


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

    # Get saved value
    exp = ResumeFresherExperience.objects.filter(user=request.user).first()

    context = {
        "exp_type": exp.type if exp else None
    }

    return render(request, 'resume/fresher_exp.html', context)

def get_experience_type(user):
    exp = ResumeFresherExperience.objects.filter(user=user).first()
    return exp.type if exp else None

@login_required
def edit_header(request):

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

    header = ResumeHeader.objects.filter(user=request.user).first()

    context = {
        "header": header,
        "exp_type": get_experience_type(request.user)
    }

    return render(request, 'resume/header.html', context)

@login_required
def edit_summary(request):
    """Step 2: Professional Summary"""

    if request.method == 'POST':

        summary_text = request.POST.get('summary')

        ResumeSummary.objects.update_or_create(
            user=request.user,
            defaults={'summary': summary_text}
        )

        # Get experience type
        exp_type = get_experience_type(request.user)

        # Redirect based on selection
        if exp_type == "experienced":
            return redirect('edit_experience')
        else:
            return redirect('edit_education')

    summary = ResumeSummary.objects.filter(user=request.user).first()

    return render(request, 'resume/summary.html', {
        'summary': summary,
        'exp_type': get_experience_type(request.user)
    })

@login_required
def ai_generate_summary(request):

    header = ResumeHeader.objects.filter(user=request.user).first()
    exp = ResumeFresherExperience.objects.filter(user=request.user).first()

    profession = header.profession if header else ""
    exp_type = exp.type if exp else "fresher"

    prompt = f"""
Generate ONLY the resume summary.

Profession: {profession}
Experience Level: {exp_type}

Rules:
- 2 to 4 lines
- ATS friendly
- Professional tone
- Do NOT add titles
- Do NOT add explanations
- Do NOT write phrases like:
  "Here is a resume summary"
  "Here is a possible summary"
- Output ONLY the summary text.
"""

    response = ollama.chat(
        model='llama3.2:1b',
        messages=[{'role':'user','content':prompt}],
        options={
            'temperature':0.6,
            'num_predict':120
        }
    )

    summary = response['message']['content'].strip()

    return JsonResponse({"summary": summary})


@login_required
def ai_optimize_summary(request):

    data = json.loads(request.body)
    summary = data.get("summary","")

    prompt = f"""
Rewrite and optimize the following resume summary.

Summary:
{summary}

Rules:
- ALWAYS rewrite the sentences using different wording
- Keep it 2-4 lines
- Improve grammar and clarity
- Make it ATS optimized
- Keep the original meaning
- Do NOT add explanations
- Output ONLY the rewritten summary
"""

    response = ollama.chat(
        model='llama3.2:1b',
        messages=[{'role':'user','content':prompt}],
        options={
            'temperature':0.4,
            'num_predict':120
        }
    )

    optimized = response['message']['content'].strip()

    return JsonResponse({"summary": optimized})

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
        selected = request.POST.get("template") or request.POST.get("template_name")
        profile_image = request.FILES.get("profile_image")

        if profile_image:
            header, created = ResumeHeader.objects.get_or_create(user=request.user)
            header.profile_image = profile_image
            header.save()

        if selected:
            ResumeTemplate.objects.update_or_create(
                user=request.user,
                defaults={"template_name": selected}
            )
            return redirect("resume_preview")
    return render(request, "resume/select_template.html")

@login_required
def resume_preview(request):
    """Step 8: Final Preview Wrapper (with ATS Sidebar)"""
    template = ResumeTemplate.objects.filter(user=request.user).first()
    return render(request, "resume/preview.html", {"template": template})

@login_required
@xframe_options_exempt
def render_resume_template(request):
    """View to render the raw resume HTML for the iframe"""
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
        # print("Extracted Raw Text:", raw_text) 

        if not raw_text:
            messages.error(request, "Could not read resume.")
            return redirect('upload_resume')

        # AI Parsing
        start_time = time.time()
        parsed = parse_resume_with_ai(raw_text)
        print("Time taken for AI parsing:", time.time() - start_time)

        # --------------------------
        # SAVE HEADER
        # --------------------------

        header = parsed.get("resume_header", {})

        ResumeHeader.objects.update_or_create(
            user=request.user,
            defaults={
                "full_name": header.get("full_name") or "",
                "profession": header.get("profession") or "",
                "email": header.get("email") or "",
                "phone": header.get("phone") or "",
                "address": header.get("address") or "",
                "linkedin": header.get("linkedin") or "",
                "github": header.get("github") or "",
                "website": header.get("website") or ""
            }
        )

        # --------------------------
        # SUMMARY
        # --------------------------

        summary = parsed.get("resume_summary", {})

        ResumeSummary.objects.update_or_create(
            user=request.user,
            defaults={
                "summary": summary.get("summary") or ""
            }
        )

        # --------------------------
        # EXPERIENCE
        # --------------------------

        ResumeExperience.objects.filter(user=request.user).delete()

        for exp in parsed.get("resume_experiences", []):

            ResumeExperience.objects.create(
                user=request.user,
                job_title=exp.get("job_title") or "",
                employer=exp.get("employer") or "",
                location=exp.get("location") or "",
                start_month=int(exp.get("start_month")) if exp.get("start_month") else None,
                start_year=int(exp.get("start_year")) if exp.get("start_year") else None,
                end_month=int(exp.get("end_month")) if exp.get("end_month") else None,
                end_year=int(exp.get("end_year")) if exp.get("end_year") else None,
                currently_working=exp.get("currently_working", False),
                description=exp.get("description") or "",
                skills=exp.get("skills") or ""
            )

        # --------------------------
        # EDUCATION
        # --------------------------

        ResumeEducation.objects.filter(user=request.user).delete()

        for edu in parsed.get("resume_education", []):

            ResumeEducation.objects.create(
                user=request.user,
                institute_name=edu.get("institute_name") or "",
                institute_location=edu.get("institute_location") or "",
                degree=edu.get("degree") or "",
                field_of_study=edu.get("field_of_study") or "",
                start_year=int(edu.get("start_year") or None) if edu.get("start_year") else None,
                end_year=int(edu.get("end_year") or None) if edu.get("end_year") else None
            )

        # --------------------------
        # SKILLS
        # --------------------------

        ResumeSkill.objects.filter(user=request.user).delete()

        for skill in parsed.get("resume_skills", []):
            ResumeSkill.objects.create(
                user=request.user,
                skill_name=skill.get("skill_name")
            )

        # --------------------------
        # ADDITIONAL
        # --------------------------
        ResumeAdditional.objects.filter(user=request.user).delete()
        for add in parsed.get("resume_additional", []):
            ResumeAdditional.objects.create(
                user=request.user,
                additional_title=add.get("additional_title") or "",
                additional_desc=add.get("additional_desc") or ""
            )



        messages.success(request, "AI extracted your resume successfully!")

        return redirect("fresher_exp")

    return render(request, 'resume/upload_resume.html')


@login_required
def ats_analyze(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            jd_text = data.get("jd", "")
            if not jd_text:
                return JsonResponse({"error": "Job Description is required."}, status=400)
                
            # Gather Resume Text
            header = ResumeHeader.objects.filter(user=request.user).first()
            summary = ResumeSummary.objects.filter(user=request.user).first()
            experiences = ResumeExperience.objects.filter(user=request.user)
            skills = ResumeSkill.objects.filter(user=request.user)
            
            resume_text = "RESUME DETAILS:\n"
            if header:
                resume_text += f"Profession: {header.profession}\n"
            if summary:
                resume_text += f"Summary: {summary.summary}\n"
            resume_text += "Skills: " + ", ".join([s.skill_name for s in skills]) + "\n"
            resume_text += "Experience:\n"
            for exp in experiences:
                resume_text += f"- {exp.job_title} at {exp.employer}. {exp.description}\n"
                
            # LOCAL ATS ATS LOGIC (No API)
            import re
            
            # Extract meaningful words
            jd_words = set([w.strip().lower() for w in re.split(r'\W+', jd_text) if len(w) > 3])
            resume_words = set([w.strip().lower() for w in re.split(r'\W+', resume_text) if len(w) > 3])
            
            common = list(jd_words.intersection(resume_words))
            missing = list(jd_words.difference(resume_words))[:6]
            matched = common[:10]
            
            score = min(98, 55 + len(matched) * 4) # Base 55 + 4 per match
            
            exp_match = "HIGH" if score >= 85 else ("MEDIUM" if score >= 70 else "LOW")
            verdict = "Candidate is a strong fit!" if score >= 80 else "Candidate needs more tailored keywords."
            
            result = {
              "ats_score": score,
              "summary": f"Your resume contains {len(matched)} direct keyword matches with the job description.",
              "matched_keywords": matched,
              "missing_keywords": missing if missing else ["Everything looks covered!"],
              "experience_match": exp_match,
              "improvement_suggestions": [
                  "Ensure your past job titles align closely with this JD.",
                  "Add concrete, quantifiable metrics to your recent roles."
              ],
              "final_verdict": verdict
            }
            return JsonResponse(result)
            
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
            
    return JsonResponse({"error": "Invalid request"}, status=400)