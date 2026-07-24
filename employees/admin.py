from django.contrib import admin

from .models import EmployeeDocument, EmployeeProfile, Notification, OnboardingStep, RequiredAction


class EmployeeDocumentInline(admin.TabularInline):
    model = EmployeeDocument
    extra = 1
    fields = ("document_type", "document_name", "verification_status", "uploaded_at")
    readonly_fields = ("uploaded_at",)


class OnboardingStepInline(admin.TabularInline):
    model = OnboardingStep
    extra = 0
    fields = ("step_name", "status", "completed_at")
    readonly_fields = ("completed_at",)


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "employee_id",
        "department",
        "designation",
        "phone_number",
        "joining_date",
        "profile_completed",
        "profile_completion_percentage",
    )
    list_filter = ("department", "profile_completed", "joining_date")
    search_fields = (
        "user__full_name",
        "user__personal_email",
        "employee_id",
        "phone_number",
    )
    list_editable = ("profile_completed", "profile_completion_percentage")
    readonly_fields = ("created_at", "updated_at")
    inlines = [EmployeeDocumentInline, OnboardingStepInline]

    fieldsets = (
        ("User Information", {"fields": ("user", "employee_id")}),
        (
            "Employment Details",
            {"fields": ("department", "designation", "joining_date")},
        ),
        (
            "Contact Information",
            {"fields": ("phone_number", "address", "date_of_birth")},
        ),
        (
            "Emergency Contact",
            {"fields": ("emergency_contact_name", "emergency_contact_phone")},
        ),
        (
            "Profile Status",
            {"fields": ("profile_completed", "profile_completion_percentage", "resume")},
        ),
        ("Timestamps", {"classes": ("collapse",), "fields": ("created_at", "updated_at")}),
    )


@admin.register(EmployeeDocument)
class EmployeeDocumentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "employee",
        "document_type",
        "document_name",
        "verification_status",
        "uploaded_at",
    )
    list_filter = ("document_type", "verification_status", "uploaded_at")
    search_fields = ("document_name", "employee__user__full_name", "employee__employee_id")
    list_editable = ("verification_status",)
    readonly_fields = ("uploaded_at",)

    fieldsets = (
        ("Document Information", {"fields": ("employee", "document_type", "document_name")}),
        ("File", {"fields": ("file",)}),
        (
            "Verification",
            {
                "fields": (
                    "verification_status",
                    "verified_by",
                    "remarks",
                )
            },
        ),
        ("Timestamp", {"fields": ("uploaded_at",)}),
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "employee", "title", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("title", "message", "employee__user__full_name")
    list_editable = ("is_read",)
    readonly_fields = ("created_at",)


@admin.register(RequiredAction)
class RequiredActionAdmin(admin.ModelAdmin):
    list_display = ("id", "employee", "title", "status", "due_date", "created_at")
    list_filter = ("status", "due_date")
    search_fields = ("title", "description", "employee__user__full_name")
    list_editable = ("status",)
    readonly_fields = ("created_at",)


@admin.register(OnboardingStep)
class OnboardingStepAdmin(admin.ModelAdmin):
    list_display = ("id", "employee", "step_name", "status", "completed_at")
    list_filter = ("step_name", "status", "completed_at")
    search_fields = ("employee__user__full_name",)
    list_editable = ("status",)
    readonly_fields = ("completed_at", "created_at")

