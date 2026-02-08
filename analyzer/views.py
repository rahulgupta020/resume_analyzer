# from django.shortcuts import render, redirect
# from .models import Resume, ResumeHeader
# from django.contrib.auth.decorators import login_required

# @login_required
# def edit_header(request, resume_id):
#     resume = Resume.objects.get(id=resume_id, user=request.user)

#     if request.method == 'POST':
#         ResumeHeader.objects.update_or_create(
#             resume=resume,
#             defaults={
#                 'full_name': request.POST['full_name'],
#                 'email': request.POST['email'],
#                 'phone': request.POST['phone'],
#                 'linkedin': request.POST.get('linkedin', ''),
#                 'github': request.POST.get('github', ''),
#             }
#         )
#         return redirect('edit_summary', resume.id)

#     return render(request, 'resume/header.html', {'resume': resume})
