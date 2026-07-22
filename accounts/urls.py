from django.urls import path
from .views import home, login_view, register_view, forgot_password

urlpatterns = [
    path("", home, name="home"),
    path("login/", login_view, name="login"),
    path("register/", register_view, name="register"),
    path("forgot-password/", forgot_password, name="forgot_password"),
]