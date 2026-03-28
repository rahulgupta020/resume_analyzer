from .models import ResumeFresherExperience

def experience_type(request):
    if request.user.is_authenticated:
        exp = ResumeFresherExperience.objects.filter(user=request.user).first()
        return {"exp_type": exp.type if exp else None}
    return {"exp_type": None}