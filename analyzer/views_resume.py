import time

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.clickjacking import xframe_options_exempt
from .models import (
    ResumeFresherExperience, ResumeHeader, ResumeSummary, 
    ResumeExperience, ResumeEducation, ResumeSkill, 
    ResumeAdditional, ResumeCustomSection, ResumeTemplate, ResumeLanguage
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
def ai_generate_additional(request):
    data = json.loads(request.body)
    title = data.get("title", "")

    prompt = f"""
Generate ONLY the project or award description for a resume.

Title: {title}

Rules:
- 2 to 4 lines
- Professional tone
- Emphasize impact and skills
- Do NOT add titles
- Do NOT add explanations
- Output ONLY the description text.
"""
    response = ollama.chat(
        model='llama3.2:1b',
        messages=[{'role':'user','content':prompt}],
        options={
            'temperature':0.6,
            'num_predict':120
        }
    )

    desc = response['message']['content'].strip()
    return JsonResponse({"description": desc})


@login_required
def ai_optimize_additional(request):
    data = json.loads(request.body)
    desc = data.get("description", "")

    prompt = f"""
Rewrite and optimize the following project or award description.

Description:
{desc}

Rules:
- ALWAYS rewrite the sentences using different wording
- Keep it 2-4 lines
- Improve grammar and clarity
- Make it ATS optimized
- Keep the original meaning
- Do NOT add explanations
- Output ONLY the rewritten description
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
    return JsonResponse({"description": optimized})


@login_required
def ai_generate_experience(request):
    data = json.loads(request.body)
    title = data.get("title", "")
    company = data.get("company", "")

    prompt = f"""
Generate ONLY the work experience description for a resume.

Job Title: {title}
Company: {company}

Rules:
- 3 to 5 bullet points
- Professional tone
- Emphasize impact and skills
- Start each bullet point with an action verb
- Do NOT add titles
- Do NOT add explanations
- Output ONLY the description text, using standard formatting (like '-' or '•').
"""
    response = ollama.chat(
        model='llama3.2:1b',
        messages=[{'role':'user','content':prompt}],
        options={
            'temperature':0.6,
            'num_predict':250
        }
    )

    desc = response['message']['content'].strip()
    return JsonResponse({"description": desc})

@login_required
def ai_optimize_experience(request):
    data = json.loads(request.body)
    desc = data.get("description", "")

    prompt = f"""
Rewrite and optimize the following work experience description.

Description:
{desc}

Rules:
- ALWAYS rewrite using different, more powerful wording
- Keep it 3-5 bullet points
- Improve grammar and clarity
- Make it ATS optimized by including action verbs
- Keep the original meaning
- Do NOT add explanations
- Output ONLY the rewritten description using standard formatting.
"""
    response = ollama.chat(
        model='llama3.2:1b',
        messages=[{'role':'user','content':prompt}],
        options={
            'temperature':0.4,
            'num_predict':250
        }
    )

    optimized = response['message']['content'].strip()
    return JsonResponse({"description": optimized})



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
                
        # Process languages
        ResumeLanguage.objects.filter(user=request.user).delete()
        lang_count = int(request.POST.get("language_count", 0))
        for i in range(lang_count):
            lang = request.POST.get(f"language_name_{i}")
            if lang:
                ResumeLanguage.objects.create(
                    user=request.user,
                    language=lang,
                    proficiency=request.POST.get(f"proficiency_{i}", "")
                )
                
        # Process custom sections
        ResumeCustomSection.objects.filter(user=request.user).delete()
        custom_count = int(request.POST.get("custom_count", 0))
        for i in range(custom_count):
            title = request.POST.get(f"custom_title_{i}")
            if title:
                ResumeCustomSection.objects.create(
                    user=request.user,
                    title=title,
                    description=request.POST.get(f"custom_desc_{i}", "")
                )
                
        return redirect("select_template")

    # ✅ FIXED: Changed filter(request.user) to filter(user=request.user)
    additionals = ResumeAdditional.objects.filter(user=request.user)
    languages = ResumeLanguage.objects.filter(user=request.user)
    custom_sections = ResumeCustomSection.objects.filter(user=request.user)
    return render(request, "resume/additional.html", {
        "additionals": additionals,
        "languages": languages,
        "custom_sections": custom_sections
    })

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
        "languages": ResumeLanguage.objects.filter(user=request.user),
        "custom_sections": ResumeCustomSection.objects.filter(user=request.user),
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
        ResumeCustomSection.objects.filter(user=request.user).delete()
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
def ats_baseline_score(request):

    header = ResumeHeader.objects.filter(user=request.user).first()
    summary = ResumeSummary.objects.filter(user=request.user).first()
    experiences = ResumeExperience.objects.filter(user=request.user)
    skills = ResumeSkill.objects.filter(user=request.user)

    resume_text = ""

    if header:
        resume_text += f"Name: {header.full_name}\n"
        resume_text += f"Profession: {header.profession}\n"
        resume_text += f"Email: {header.email}\n"
        resume_text += f"Phone: {header.phone}\n"

    if summary:
        resume_text += f"Summary: {summary.summary}\n"

    resume_text += "Skills: " + ", ".join([s.skill_name for s in skills]) + "\n"

    for exp in experiences:
        resume_text += f"{exp.job_title} at {exp.employer}. {exp.description}\n"


    prompt = f"""
You are an ATS resume analyzer.

Analyze the resume and evaluate:

1. Contact Information
2. ATS Friendly Structure
3. Skills and Keywords
4. Summary Quality
5. Experience Impact

Also detect missing industry keywords.

Resume:
{resume_text}

Return JSON ONLY:

{{
"ats_score": number between 0-100,
"layout": "good or bad",
"contact": "good or missing",
"summary": "good or weak",
"keywords": "good or weak",
"missing_keywords": ["keyword1","keyword2","keyword3"],
"suggestions": ["tip1","tip2","tip3"]
}}
"""

    response = ollama.chat(
        model="llama3.2:1b",
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0.2}
    )

    content = response["message"]["content"]

    try:
        data = json.loads(content)
    except:
        data = {
            "ats_score": 65,
            "layout": "good",
            "contact": "good",
            "summary": "weak",
            "keywords": "weak",
            "missing_keywords": ["Python", "FastAPI", "Docker"],
            "suggestions": [
                "Add measurable achievements in experience section",
                "Include more industry keywords",
                "Strengthen professional summary"
            ]
        }

    return JsonResponse(data)


import json
import re
import ollama

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required
def ats_analyze(request):

    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=400)

    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    jd_text = data.get("jd", "")

    header = ResumeHeader.objects.filter(user=request.user).first()
    summary = ResumeSummary.objects.filter(user=request.user).first()
    experiences = ResumeExperience.objects.filter(user=request.user)
    skills = ResumeSkill.objects.filter(user=request.user)

    resume_text = ""

    if header:
        resume_text += f"Profession: {header.profession}\n"

    if summary:
        resume_text += f"Summary: {summary.summary}\n"

    if skills.exists():
        resume_text += "Skills: " + ", ".join([s.skill_name for s in skills]) + "\n"

    for exp in experiences:
        resume_text += f"{exp.job_title} at {exp.employer}. {exp.description}\n"


    # ----------------------------
    # AI PROMPT
    # ----------------------------
    prompt = f"""
You are an ATS resume analyzer.

Compare the resume with the job description.

Return ONLY valid JSON.

Rules:
- matched_keywords must contain ONLY keywords present in BOTH resume and job description
- missing_keywords must contain ONLY keywords present in job description but NOT in resume
- Keywords must be short (1-3 words)
- Do NOT write sentences inside keyword arrays
- ats_score must be between 0 and 100

IMPORTANT RULES:
- Output must start with {{ and end with }}
- Do NOT write explanations
- Do NOT write text before JSON
- Do NOT write text after JSON


RESUME:
{resume_text}

JOB DESCRIPTION:
{jd_text}

Return JSON ONLY:

{{
"ats_score": 0,
"matched_keywords": ["keyword1","keyword2"],
"missing_keywords": ["keyword1","keyword2"],
"improvement_suggestions": ["tip1","tip2"],
"final_verdict": "short verdict sentence"
}}
"""


    # ----------------------------
    # CALL OLLAMA
    # ----------------------------
    response = ollama.chat(
        model="llama3.2:1b",
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0.2}
    )

    content = response["message"]["content"]
    # print("RAW CONTENT:\n", content)

    # ----------------------------
    # CLEAN RESPONSE
    # ----------------------------
    try:
        # Extract JSON if extra text exists
        json_match = re.search(r"\{[\s\S]*\}", content)
        if json_match:
            result = json.loads(json_match.group())
        else:
            raise ValueError("No JSON found")

        # print("JSON MATCH:\n", json_match.group() if json_match else "None")

    except Exception:
        result = {
            "ats_score": 60,
            "matched_keywords": [],
            "missing_keywords": ["Python", "SQL", "Communication"],
            "improvement_suggestions": [
                "Add more technical skills",
                "Highlight measurable achievements",
                "Improve resume summary"
            ],
            "final_verdict": "AI parsing failed but resume analysis fallback applied"
        }

    # ----------------------------
    # SAFETY FIXES
    # ----------------------------

    if not result.get("matched_keywords"):
        result["matched_keywords"] = []

    if not result.get("missing_keywords"):
        result["missing_keywords"] = ["Add more relevant keywords"]

    if not result.get("improvement_suggestions"):
        result["improvement_suggestions"] = [
            "Add more relevant technical skills",
            "Improve project descriptions"
        ]

    if not result.get("final_verdict"):
        result["final_verdict"] = "Resume partially matches the job description"

    if not result.get("ats_score"):
        result["ats_score"] = 60

    return JsonResponse(result)