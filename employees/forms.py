from django import forms
from django.core.exceptions import ValidationError

from .models import EmployeeDocument, EmployeeProfile


class ProfileForm(forms.ModelForm):
    """Form for employees to complete/edit their profile."""

    class Meta:
        model = EmployeeProfile
        fields = [
            "phone_number",
            "address",
            "date_of_birth",
            "emergency_contact_name",
            "emergency_contact_phone",
            "resume",
        ]
        widgets = {
            "phone_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter phone number",
                    "type": "tel",
                }
            ),
            "address": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Enter full address",
                }
            ),
            "date_of_birth": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "emergency_contact_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Emergency contact person name",
                }
            ),
            "emergency_contact_phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Emergency contact phone number",
                    "type": "tel",
                }
            ),
            "resume": forms.FileInput(
                attrs={
                    "class": "form-control",
                    "accept": ".pdf,.doc,.docx",
                }
            ),
        }

    def clean_phone_number(self):
        phone = self.cleaned_data.get("phone_number")
        if phone and len(phone) < 10:
            raise ValidationError("Phone number must be at least 10 digits.")
        return phone

    def clean_emergency_contact_phone(self):
        phone = self.cleaned_data.get("emergency_contact_phone")
        if phone and len(phone) < 10:
            raise ValidationError("Emergency contact phone must be at least 10 digits.")
        return phone


class DocumentUploadForm(forms.ModelForm):
    """Form for employees to upload documents."""

    class Meta:
        model = EmployeeDocument
        fields = ["document_type", "document_name", "file"]
        widgets = {
            "document_type": forms.Select(attrs={"class": "form-select"}),
            "document_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Document name (e.g., Updated Resume)",
                }
            ),
            "file": forms.FileInput(
                attrs={
                    "class": "form-control",
                    "accept": ".pdf,.jpg,.jpeg,.png,.doc,.docx",
                }
            ),
        }

    def clean_file(self):
        file = self.cleaned_data.get("file")
        if file:
            max_size = 10 * 1024 * 1024  # 10MB
            if file.size > max_size:
                raise ValidationError("File size must be under 10MB.")
        return file


class SettingsForm(forms.Form):
    """Form for employee notification preferences."""

    email_notifications = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input", "role": "switch"}),
    )
    document_reminders = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input", "role": "switch"}),
    )
    weekly_summary = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input", "role": "switch"}),
    )


class EmployeeApprovalForm(forms.Form):
    """Form for HR/Admin to approve employees."""

    employee_id = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "EMP-XXXXXX"}
        ),
    )
    company_email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "first.last@company.com",
            }
        )
    )
    temporary_password = forms.CharField(
        max_length=128,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Generated temporary password",
            }
        ),
    )

