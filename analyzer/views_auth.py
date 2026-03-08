from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
# ✅ FIX: Added the missing decorator import
from django.contrib.auth.decorators import login_required 

def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'auth/signup.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return render(request, 'auth/signup.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, 'auth/signup.html')

        User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        messages.success(request, "Account created successfully. Please log in.")
        return redirect('login')
    return render(request, 'auth/signup.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Convert email → username
        try:
            user_obj = User.objects.get(email=email)
            username = user_obj.username
            
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid email or password")
        except User.DoesNotExist:
            messages.error(request, "Invalid email or password")

    return render(request, 'auth/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

# ✅ Step-by-Step Dashboard / Account View
@login_required
def my_accounts(request):
    """
    Renders the 'My Accounts' page. 
    Requires the user to be logged in.
    """
    return render(request, 'base/myaccounts.html')