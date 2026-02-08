from .models import ResumeFresherExperience

def resume_experience_context(request):
    if request.user.is_authenticated:
        try:
            obj = ResumeFresherExperience.objects.get(user=request.user)
            return {
                'experience_type': obj.type
            }
        except ResumeFresherExperience.DoesNotExist:
            return {
                'experience_type': None
            }

    return {}
