from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

from .models import EmployeeDocument, EmployeeProfile


class ProfileForm(forms.ModelForm):
    """Enhanced profile form with all fields."""

    class Meta:
        model = EmployeeProfile
        fields = [
            "phone_number",
            "alternate_number",
            "date_of_birth",
            "gender",
            "reporting_manager",
            "current_address",
            "permanent_address",
            "city",
            "state",
            "country",
            "pincode",
            "emergency_contact_name",
            "emergency_contact_phone",
            "emergency_contact_relationship",
            "profile_picture",
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
            "alternate_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter alternate phone number",
                    "type": "tel",
                }
            ),
            "date_of_birth": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "gender": forms.Select(attrs={"class": "form-select"}),
            "reporting_manager": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter reporting manager name",
                }
            ),
            "current_address": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Enter current address",
                }
            ),
            "permanent_address": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Enter permanent address",
                }
            ),
            "city": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter city"}
            ),
            "state": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter state"}
            ),
            "country": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter country"}
            ),
            "pincode": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter pincode",
                    "maxlength": "10",
                }
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
            "emergency_contact_relationship": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g., Spouse, Parent, Sibling",
                }
            ),
            "profile_picture": forms.FileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/*",
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

    def clean_alternate_number(self):
        phone = self.cleaned_data.get("alternate_number")
        if phone and len(phone) < 10:
            raise ValidationError("Alternate phone number must be at least 10 digits.")
        return phone

    def clean_emergency_contact_phone(self):
        phone = self.cleaned_data.get("emergency_contact_phone")
        if phone and len(phone) < 10:
            raise ValidationError("Emergency contact phone must be at least 10 digits.")
        return phone

    def clean_profile_picture(self):
        picture = self.cleaned_data.get("profile_picture")
        if picture:
            max_size = 5 * 1024 * 1024  # 5MB
            if picture.size > max_size:
                raise ValidationError("Profile picture size must be under 5MB.")
            if not picture.content_type.startswith("image/"):
                raise ValidationError("File must be an image.")
        return picture


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
            ext = file.name.split(".")[-1].lower()
            allowed = ["pdf", "jpg", "jpeg", "png", "doc", "docx"]
            if ext not in allowed:
                raise ValidationError(
                    f"File type '.{ext}' is not allowed. Allowed types: {', '.join(allowed)}"
                )
        return file


class DocumentReplaceForm(forms.ModelForm):
    """Form for replacing an existing document."""

    class Meta:
        model = EmployeeDocument
        fields = ["file"]
        widgets = {
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
            max_size = 10 * 1024 * 1024
            if file.size > max_size:
                raise ValidationError("File size must be under 10MB.")
            ext = file.name.split(".")[-1].lower()
            allowed = ["pdf", "jpg", "jpeg", "png", "doc", "docx"]
            if ext not in allowed:
                raise ValidationError(f"File type '.{ext}' is not allowed.")
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

