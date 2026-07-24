from django.db import models
from accounts.models import User


class EmployeeProfile(models.Model):

    DEPARTMENT_CHOICES = (
        ("IT", "IT"),
        ("HR", "HR"),
        ("Finance", "Finance"),
        ("Marketing", "Marketing"),
        ("Operations", "Operations"),
        ("Sales", "Sales"),
        ("Engineering", "Engineering"),
    )

    GENDER_CHOICES = (
        ("MALE", "Male"),
        ("FEMALE", "Female"),
        ("OTHER", "Other"),
        ("PREFER_NOT_TO_SAY", "Prefer not to say"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="employee_profile")

    employee_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES, blank=True, null=True)
    designation = models.CharField(max_length=100, blank=True, null=True)
    reporting_manager = models.CharField(max_length=150, blank=True, null=True)

    # Personal Information
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    alternate_number = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True, null=True)
    joining_date = models.DateField(blank=True, null=True)

    # Address Information
    current_address = models.TextField(blank=True, null=True)
    permanent_address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)

    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=150, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True, null=True)
    emergency_contact_relationship = models.CharField(max_length=100, blank=True, null=True)

    # Profile Picture
    profile_picture = models.ImageField(upload_to="profile_pictures/", blank=True, null=True)

    # Resume & Status
    resume = models.FileField(upload_to="resumes/", blank=True, null=True)
    profile_completed = models.BooleanField(default=False)
    profile_completion_percentage = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.full_name} ({self.employee_id})"

    class Meta:
        ordering = ["-created_at"]


class EmployeeDocument(models.Model):

    DOCUMENT_TYPES = (
        ("RESUME", "Resume"),
        ("AADHAAR", "Aadhaar Card"),
        ("PAN", "PAN Card"),
        ("PHOTO", "Passport Photo"),
        ("DEGREE", "Degree Certificate"),
        ("EXPERIENCE", "Experience Letter"),
        ("OFFER_LETTER", "Offer Letter"),
        ("OTHER", "Other"),
    )

    VERIFICATION_STATUS = (
        ("PENDING", "Pending"),
        ("VERIFIED", "Verified"),
        ("REJECTED", "Rejected"),
    )

    employee = models.ForeignKey(
        EmployeeProfile, on_delete=models.CASCADE, related_name="documents"

    )

    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPES, default="OTHER")
    document_name = models.CharField(max_length=100)
    file = models.FileField(upload_to="documents/")
    file_size = models.PositiveIntegerField(default=0, help_text="File size in bytes")

    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    verification_status = models.CharField(
        max_length=20, choices=VERIFICATION_STATUS, default="PENDING"
    )
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_documents",
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.document_name} - {self.employee.user.full_name}"

    def get_file_extension(self):
        import os
        return os.path.splitext(self.file.name)[1].lower() if self.file else ""

    def is_image(self):
        return self.get_file_extension() in [".jpg", ".jpeg", ".png", ".gif", ".webp"]

    def is_pdf(self):
        return self.get_file_extension() == ".pdf"


class Notification(models.Model):

    CATEGORY_CHOICES = (
        ("PROFILE", "Profile"),
        ("DOCUMENT", "Documents"),
        ("APPROVAL", "Approval"),
        ("SYSTEM", "System"),
    )

    employee = models.ForeignKey(
        EmployeeProfile, on_delete=models.CASCADE, related_name="notifications"
    )
    title = models.CharField(max_length=200)
    message = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="SYSTEM")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        return self.title


class RequiredAction(models.Model):

    PRIORITY_CHOICES = (
        ("LOW", "Low"),
        ("MEDIUM", "Medium"),
        ("HIGH", "High"),
        ("URGENT", "Urgent"),
    )

    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("COMPLETED", "Completed"),
        ("OVERDUE", "Overdue"),
    )

    employee = models.ForeignKey(
        EmployeeProfile, on_delete=models.CASCADE, related_name="required_actions"
    )
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="MEDIUM")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    due_date = models.DateField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["status", "due_date"]
        verbose_name = "Required Action"
        verbose_name_plural = "Required Actions"

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"


class OnboardingStep(models.Model):

    STEP_CHOICES = (
        ("PROFILE_COMPLETION", "Complete Profile"),
        ("DOCUMENT_UPLOAD", "Upload Documents"),
        ("DOCUMENT_VERIFICATION", "Document Verification"),
        ("HR_APPROVAL", "HR Approval"),
        ("MANAGER_APPROVAL", "Manager Approval"),
        ("ADMIN_APPROVAL", "Admin Approval"),
        ("COMPLETED", "Onboarding Completed"),
    )

    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("IN_PROGRESS", "In Progress"),
        ("COMPLETED", "Completed"),
    )

    employee = models.ForeignKey(
        EmployeeProfile, on_delete=models.CASCADE, related_name="onboarding_steps"
    )
    step_name = models.CharField(max_length=50, choices=STEP_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    completed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        unique_together = ["employee", "step_name"]
        verbose_name = "Onboarding Step"
        verbose_name_plural = "Onboarding Steps"

    def __str__(self):
        return f"{self.get_step_name_display()} - {self.get_status_display()}"

