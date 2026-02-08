from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import ResumeFresherExperience, ResumeHeader, ResumeSummary, ResumeExperience, ResumeEducation, ResumeSkill, ResumeAdditional, ResumeTemplate

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

@login_required
def fresher_exp(request):
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
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        profession = request.POST.get('profession')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        linkedin = request.POST.get('linkedin')
        github = request.POST.get('github')
        website = request.POST.get('website')

        ResumeHeader.objects.update_or_create(
            user=request.user,
            defaults={
                'full_name': full_name,
                'profession': profession,
                'email': email,
                'phone': phone,
                'address': address,
                'linkedin': linkedin,
                'github': github,
                'website': website
            }
        )
        return redirect('edit_summary')
    try:
        header = ResumeHeader.objects.get(user=request.user)
    except ResumeHeader.DoesNotExist:
        header = None
    return render(request, 'resume/header.html', {'header': header})

@login_required
def edit_summary(request):
    if request.method == 'POST':
        summary_text = request.POST.get('summary')
        ResumeSummary.objects.update_or_create(
            user=request.user,
            defaults={'summary': summary_text}
        )
        return redirect('edit_experience')
    try:
        summary = ResumeSummary.objects.get(user=request.user)
    except ResumeSummary.DoesNotExist:
        summary = None
    return render(request, 'resume/summary.html', {'summary': summary})

@login_required
def edit_experience(request):
    if request.method == 'POST':
        ResumeExperience.objects.filter(user=request.user).delete()

        total = int(request.POST.get('experience_count', 0))

        for i in range(total):
            job_title = request.POST.get(f'job_title_{i}')
            employer = request.POST.get(f'employer_{i}')
            location = request.POST.get(f'location_{i}')
            start_month = request.POST.get(f'start_month_{i}')
            start_year = request.POST.get(f'start_year_{i}')
            end_month = request.POST.get(f'end_month_{i}') or None
            end_year = request.POST.get(f'end_year_{i}') or None
            description = request.POST.get(f'description_{i}')
            skills = request.POST.get(f'skills_{i}')

            currently_working = request.POST.get(f'currently_working_{i}') == 'on'

            # Skip empty cards (safety)
            if not job_title or not employer:
                continue

            ResumeExperience.objects.create(
                user=request.user,
                job_title=job_title,
                employer=employer,
                location=location,
                start_month=start_month,
                start_year=start_year,
                end_month=None if currently_working else int(end_month) if end_month else None,
                end_year=None if currently_working else int(end_year) if end_year else None,
                currently_working=currently_working,
                description=description,
                skills=skills
            )

        return redirect('edit_education')

    experiences = ResumeExperience.objects.filter(user=request.user)
    return render(request, 'resume/experience.html', {'experiences': experiences})

@login_required
def edit_education(request):
    if request.method == 'POST':
        ResumeEducation.objects.filter(user=request.user).delete()

        total = int(request.POST.get('education_count', 0))

        for i in range(total):
            institute_name = request.POST.get(f'institute_name_{i}')
            institute_location = request.POST.get(f'institute_location_{i}')
            degree = request.POST.get(f'degree_{i}')
            field_of_study = request.POST.get(f'field_of_study_{i}')
            start_year = request.POST.get(f'start_year_{i}')
            end_year = request.POST.get(f'end_year_{i}')

            # Skip empty cards
            if not institute_name or not degree:
                continue

            ResumeEducation.objects.create(
                user=request.user,
                institute_name=institute_name,
                institute_location=institute_location,
                degree=degree,
                field_of_study=field_of_study,
                start_year=int(start_year),
                end_year=int(end_year),
            )

        return redirect('edit_skills')

    educations = ResumeEducation.objects.filter(user=request.user)
    return render(request, 'resume/education.html', {
        'educations': educations
    })

@login_required
def edit_skills(request):
    if request.method == 'POST':
        # Delete old skills
        ResumeSkill.objects.filter(user=request.user).delete()

        total = int(request.POST.get('skill_count', 0))

        for i in range(total):
            skill_name = request.POST.get(f'skill_name_{i}')

            if skill_name:   # skip empty
                ResumeSkill.objects.create(
                    user=request.user,
                    skill_name=skill_name.strip()
                )

        return redirect('edit_additional')

    skills = ResumeSkill.objects.filter(user=request.user)

    return render(request, 'resume/skills.html', {
        'skills': skills
    })

@login_required
def edit_additional(request):

    if request.method == "POST":
        count = int(request.POST.get("additional_count", 0))

        # Delete old records
        ResumeAdditional.objects.filter(user=request.user).delete()

        for i in range(count):
            title = request.POST.get(f"additional_title_{i}")
            desc = request.POST.get(f"additional_desc_{i}")

            if title:
                ResumeAdditional.objects.create(
                    user=request.user,
                    additional_title=title,
                    additional_desc=desc
                )

        return redirect("select_template")

    additionals = ResumeAdditional.objects.filter(user=request.user)

    context = {
        "additionals": additionals
    }

    return render(request, "resume/additional.html", context)

@login_required
def select_template(request):

    if request.method == "POST":
        selected = request.POST.get("template")

        ResumeTemplate.objects.update_or_create(
            user=request.user,
            defaults={"template_name": selected}
        )

        return redirect("resume_preview")

    return render(request, "resume/select_template.html")

@login_required
def resume_preview(request):

    header = ResumeHeader.objects.filter(user=request.user).first()
    summary = ResumeSummary.objects.filter(user=request.user).first()
    experiences = ResumeExperience.objects.filter(user=request.user)
    educations = ResumeEducation.objects.filter(user=request.user)
    skills = ResumeSkill.objects.filter(user=request.user)
    additionals = ResumeAdditional.objects.filter(user=request.user)
    template = ResumeTemplate.objects.filter(user=request.user).first()

    context = {
        "header": header,
        "summary": summary,
        "experiences": experiences,
        "educations": educations,
        "skills": skills,
        "additionals": additionals,
        "template": template
    }

    if template and template.template_name == "template2":
        return render(request, "resume/templates/template2.html", context)

    elif template and template.template_name == "template3":
        return render(request, "resume/templates/template3.html", context)

    return render(request, "resume/templates/template1.html", context)
