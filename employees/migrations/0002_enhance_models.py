"""Migration to enhance EmployeeProfile, EmployeeDocument, Notification, and OnboardingStep models."""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("employees", "0001_initial"),
    ]

    operations = [
        # EmployeeProfile enhancements
        migrations.AddField(
            model_name="employeeprofile",
            name="alternate_number",
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AddField(
            model_name="employeeprofile",
            name="gender",
            field=models.CharField(
                blank=True,
                choices=[
                    ("MALE", "Male"),
                    ("FEMALE", "Female"),
                    ("OTHER", "Other"),
                    ("PREFER_NOT_TO_SAY", "Prefer not to say"),
                ],
                max_length=20,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="employeeprofile",
            name="reporting_manager",
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AddField(
            model_name="employeeprofile",
            name="current_address",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="employeeprofile",
            name="permanent_address",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="employeeprofile",
            name="city",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="employeeprofile",
            name="state",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="employeeprofile",
            name="country",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="employeeprofile",
            name="pincode",
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name="employeeprofile",
            name="emergency_contact_relationship",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="employeeprofile",
            name="profile_picture",
            field=models.ImageField(blank=True, null=True, upload_to="profile_pictures/"),
        ),
        # EmployeeDocument enhancements
        migrations.AlterField(
            model_name="employeedocument",
            name="document_type",
            field=models.CharField(
                choices=[
                    ("RESUME", "Resume"),
                    ("AADHAAR", "Aadhaar Card"),
                    ("PAN", "PAN Card"),
                    ("PHOTO", "Passport Photo"),
                    ("DEGREE", "Degree Certificate"),
                    ("EXPERIENCE", "Experience Letter"),
                    ("OFFER_LETTER", "Offer Letter"),
                    ("OTHER", "Other"),
                ],
                default="OTHER",
                max_length=30,
            ),
        ),
        migrations.AddField(
            model_name="employeedocument",
            name="file_size",
            field=models.PositiveIntegerField(default=0, help_text="File size in bytes"),
        ),
        migrations.AddField(
            model_name="employeedocument",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name="employeedocument",
            name="verified_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        # Notification enhancements
        migrations.AddField(
            model_name="notification",
            name="category",
            field=models.CharField(
                choices=[
                    ("PROFILE", "Profile"),
                    ("DOCUMENT", "Documents"),
                    ("APPROVAL", "Approval"),
                    ("SYSTEM", "System"),
                ],
                default="SYSTEM",
                max_length=20,
            ),
        ),
        migrations.AlterModelOptions(
            name="notification",
            options={
                "ordering": ["-created_at"],
                "verbose_name": "Notification",
                "verbose_name_plural": "Notifications",
            },
        ),
        # RequiredAction enhancements
        migrations.AddField(
            model_name="requiredaction",
            name="priority",
            field=models.CharField(
                choices=[
                    ("LOW", "Low"),
                    ("MEDIUM", "Medium"),
                    ("HIGH", "High"),
                    ("URGENT", "Urgent"),
                ],
                default="MEDIUM",
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name="requiredaction",
            name="completed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterModelOptions(
            name="requiredaction",
            options={
                "ordering": ["status", "due_date"],
                "verbose_name": "Required Action",
                "verbose_name_plural": "Required Actions",
            },
        ),
        # OnboardingStep enhancements
        migrations.AlterField(
            model_name="onboardingstep",
            name="step_name",
            field=models.CharField(
                choices=[
                    ("PROFILE_COMPLETION", "Complete Profile"),
                    ("DOCUMENT_UPLOAD", "Upload Documents"),
                    ("DOCUMENT_VERIFICATION", "Document Verification"),
                    ("HR_APPROVAL", "HR Approval"),
                    ("MANAGER_APPROVAL", "Manager Approval"),
                    ("ADMIN_APPROVAL", "Admin Approval"),
                    ("COMPLETED", "Onboarding Completed"),
                ],
                max_length=50,
            ),
        ),
        migrations.AlterModelOptions(
            name="onboardingstep",
            options={
                "ordering": ["created_at"],
                "verbose_name": "Onboarding Step",
                "verbose_name_plural": "Onboarding Steps",
            },
        ),
    ]

