from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import User


class RegisterForm(forms.Form):
    full_name = forms.CharField(max_length=150)
    email = forms.EmailField()
    password1 = forms.CharField(widget=forms.PasswordInput, min_length=8)
    password2 = forms.CharField(widget=forms.PasswordInput, min_length=8)

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(personal_email__iexact=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match.")

        if password1:
            validate_password(password1)

        return cleaned_data


class LoginForm(forms.Form):
    personal_email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    remember_me = forms.BooleanField(required=False)

    def clean_personal_email(self):
        return self.cleaned_data["personal_email"].strip().lower()

    def clean(self):
        cleaned_data = super().clean()
        personal_email = cleaned_data.get("personal_email")
        password = cleaned_data.get("password")

        if personal_email and password:
            self.user = authenticate(username=personal_email, password=password)

            if not self.user or not self.user.is_active:
                raise ValidationError("Invalid Email or Password")

        return cleaned_data


class ForgotPasswordForm(forms.Form):
    company_email = forms.EmailField()

    def clean_company_email(self):
        email = self.cleaned_data["company_email"].strip().lower()
        if not User.objects.filter(company_email__iexact=email).exists():
            raise ValidationError("No active account found with this company email.")
        return email


class ResetPasswordForm(forms.Form):
    new_password1 = forms.CharField(widget=forms.PasswordInput, min_length=8)
    new_password2 = forms.CharField(widget=forms.PasswordInput, min_length=8)

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("new_password1")
        p2 = cleaned_data.get("new_password2")

        if p1 and p2 and p1 != p2:
            raise ValidationError("Passwords do not match.")

        if p1:
            validate_password(p1)

        return cleaned_data