from django.urls import path

from .views import (
    ForgotPasswordView,
    HomeView,
    LoginView,
    LogoutView,
    RegisterView,
   
)

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot_password"),
    ]