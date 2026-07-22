from django.shortcuts import render

# Create your views here.

def home(request):
    return render(request, 'home.html')

def login_view(request):
    return render(request, 'accounts/login.html')

def register_view(request):
    return render(request, 'accounts/register.html')

def forgot_password(request):
    return render(request, 'accounts/forgot_password.html')
