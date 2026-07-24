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

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="employee_profile")

    employee_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES, blank=True, null=True)
    designation = models.CharField(max_length=100, blank=True, null=True)

    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    joining_date = models.DateField(blank=True, null=True)

    emergency_contact_name = models.CharField(max_length=150, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True, null=True)

    profile_completed = models.BooleanField(default=False)
    profile_completion_percentage = models.IntegerField(default=0)

    resume = models.FileField(upload_to="resumes/", blank=True, null=True)
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
        ("DEGREE", "Degree Certificate"),
        ("PHOTO", "Profile Photo"),
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

    uploaded_at = models.DateTimeField(auto_now_add=True)

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
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.document_name} - {self.employee.user.full_name}"


class Notification(models.Model):

    employee = models.ForeignKey(
        EmployeeProfile, on_delete=models.CASCADE, related_name="notifications"
    )
    title = models.CharField(max_length=200)
    message = models.TextField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class RequiredAction(models.Model):

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
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    due_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["status", "due_date"]

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"


class OnboardingStep(models.Model):

    STEP_CHOICES = (
        ("PROFILE_COMPLETION", "Complete Profile"),
        ("DOCUMENT_UPLOAD", "Upload Documents"),
        ("DOCUMENT_VERIFICATION", "Document Verification"),
        ("HR_APPROVAL", "HR Approval"),
        ("MANAGER_APPROVAL", "Manager Approval"),
        ("WELCOME_KIT", "Welcome Kit Release"),
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

    def __str__(self):
        return f"{self.get_step_name_display()} - {self.get_status_display()}"

