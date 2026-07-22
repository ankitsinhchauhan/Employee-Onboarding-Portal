from django.urls import path

from .views import (
    CompleteProfileView,
    DocumentUploadView,
    ForgotPasswordView,
    LoginView,
    LogoutView,
    PreOnboardingDashboardView,
    RegisterView,
    VerificationStatusView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot_password"),
    path("pre-onboarding/dashboard/", PreOnboardingDashboardView.as_view(), name="pre_onboarding_dashboard"),
    path("profile/complete/", CompleteProfileView.as_view(), name="complete_profile"),
    path("documents/upload/", DocumentUploadView.as_view(), name="document_upload"),
    path("verification-status/", VerificationStatusView.as_view(), name="verification_status"),
]