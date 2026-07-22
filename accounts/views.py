from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View

from .forms import ForgotPasswordForm, LoginForm, RegisterForm
from .models import User


class RegisterView(View):
    template_name = "accounts/register.html"

    def get(self, request):
        return render(request, self.template_name, {"form": RegisterForm()})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User(
                full_name=form.cleaned_data["full_name"],
                personal_email=form.cleaned_data["email"],
                # mobile_number=form.cleaned_data.get("mobile_number"),
                status=User.Status.PENDING,
                role=User.Role.UNASSIGNED,
                is_active=True,
            )
            user.set_password(form.cleaned_data["password1"])
            user.save()
            messages.success(request, "Registration successful")
            return redirect("login")

        return render(request, self.template_name, {"form": form})


class LoginView(View):
    template_name = "accounts/login.html"

    def get(self, request):
        return render(request, self.template_name, {"form": LoginForm()})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.user
            login(request, user)

            if form.cleaned_data.get("remember_me"):
                request.session.set_expiry(1209600)
            else:
                request.session.set_expiry(0)

            messages.success(request, "Login successful")
            return redirect("pre_onboarding_dashboard")

        messages.error(request, "Invalid Email or Password")
        return render(request, self.template_name, {"form": form})


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("login")

    def post(self, request):
        logout(request)
        return redirect("login")


class ForgotPasswordView(View):
    template_name = "accounts/forgot_password.html"

    def get(self, request):
        return render(request, self.template_name, {"form": ForgotPasswordForm()})

    def post(self, request):
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            messages.success(request, "Password reset link sent successfully")
            return redirect("login")
        return render(request, self.template_name, {"form": form})


class PreOnboardingDashboardView(LoginRequiredMixin, View):
    template_name = "onboarding/pre_onboarding_dashboard.html"
    login_url = "login"

    def get(self, request):
        user = request.user
        context = {
            "profile_completion": int(getattr(user, "profile_completion_percentage", 0) or 0),
            "document_completion": int(getattr(user, "document_completion_percentage", 0) or 0),
            "verification_status": getattr(user, "verification_status", "Pending") or "Pending",
            "overall_status": getattr(user, "status", "Pending") or "Pending",
        }
        context["progress_total"] = int((context["profile_completion"] + context["document_completion"]) / 2)
        return render(request, self.template_name, context)


class CompleteProfileView(LoginRequiredMixin, View):
    template_name = "onboarding/complete_profile.html"
    login_url = "login"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        messages.success(request, "Profile saved successfully")
        return redirect("pre_onboarding_dashboard")


class DocumentUploadView(LoginRequiredMixin, View):
    template_name = "onboarding/document_upload.html"
    login_url = "login"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        messages.success(request, "Document uploaded successfully")
        return redirect("pre_onboarding_dashboard")


class VerificationStatusView(LoginRequiredMixin, View):
    template_name = "onboarding/verification_status.html"
    login_url = "login"

    def get(self, request):
        return render(request, self.template_name)