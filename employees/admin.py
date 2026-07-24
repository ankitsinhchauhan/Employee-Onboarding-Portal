from django.contrib import admin

from .models import EmployeeDocument, EmployeeProfile, Notification, OnboardingStep, RequiredAction


class EmployeeDocumentInline(admin.TabularInline):
    model = EmployeeDocument
    extra = 1
    fields = ("document_type", "document_name", "file_size", "verification_status", "uploaded_at")
    readonly_fields = ("uploaded_at", "file_size")


class OnboardingStepInline(admin.TabularInline):
    model = OnboardingStep
    extra = 0
    fields = ("step_name", "status", "completed_at")
    readonly_fields = ("completed_at",)


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id", "user", "employee_id", "department", "designation",
        "phone_number", "joining_date", "profile_completed",
        "profile_completion_percentage",
    )
    list_filter = ("department", "profile_completed", "joining_date", "gender")
    search_fields = (
        "user__full_name", "user__personal_email", "employee_id",
        "phone_number", "city", "state",
    )
    list_editable = ("profile_completed", "profile_completion_percentage")
    readonly_fields = ("created_at", "updated_at")
    inlines = [EmployeeDocumentInline, OnboardingStepInline]

    fieldsets = (
        ("User Information", {"fields": ("user", "employee_id")}),
        ("Employment Details", {
            "fields": ("department", "designation", "joining_date", "reporting_manager"),
        }),
        ("Personal Information", {
            "fields": ("phone_number", "alternate_number", "date_of_birth", "gender"),
        }),
        ("Address Information", {
            "fields": ("current_address", "permanent_address", "city", "state", "country", "pincode"),
        }),
        ("Emergency Contact", {
            "fields": ("emergency_contact_name", "emergency_contact_phone", "emergency_contact_relationship"),
        }),
        ("Profile Media", {
            "fields": ("profile_picture", "resume"),
        }),
        ("Profile Status", {
            "fields": ("profile_completed", "profile_completion_percentage"),
        }),
        ("Timestamps", {
            "classes": ("collapse",),
            "fields": ("created_at", "updated_at"),
        }),
    )


@admin.register(EmployeeDocument)
class EmployeeDocumentAdmin(admin.ModelAdmin):
    list_display = (
        "id", "employee", "document_type", "document_name",
        "file_size_display", "verification_status", "uploaded_at",
    )
    list_filter = ("document_type", "verification_status", "uploaded_at")
    search_fields = ("document_name", "employee__user__full_name", "employee__employee_id")
    list_editable = ("verification_status",)
    readonly_fields = ("uploaded_at", "updated_at", "file_size")

    fieldsets = (
        ("Document Information", {"fields": ("employee", "document_type", "document_name")}),
        ("File", {"fields": ("file", "file_size")}),
        ("Verification", {
            "fields": ("verification_status", "verified_by", "verified_at", "remarks"),
        }),
        ("Timestamps", {"classes": ("collapse",), "fields": ("uploaded_at", "updated_at")}),
    )

    def file_size_display(self, obj):
        if not obj.file_size:
            return "—"
        for unit in ["B", "KB", "MB", "GB"]:
            if obj.file_size < 1024:
                return f"{obj.file_size:.1f} {unit}"
            obj.file_size /= 1024
        return f"{obj.file_size:.1f} TB"
    file_size_display.short_description = "File Size"


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "employee", "title", "category", "is_read", "created_at")
    list_filter = ("is_read", "category", "created_at")
    search_fields = ("title", "message", "employee__user__full_name")
    list_editable = ("is_read",)
    readonly_fields = ("created_at",)

    fieldsets = (
        ("Notification", {"fields": ("employee", "title", "message")}),
        ("Status", {"fields": ("category", "is_read")}),
        ("Timestamp", {"fields": ("created_at",)}),
    )


@admin.register(RequiredAction)
class RequiredActionAdmin(admin.ModelAdmin):
    list_display = ("id", "employee", "title", "priority", "status", "due_date", "created_at")
    list_filter = ("status", "priority", "due_date")
    search_fields = ("title", "description", "employee__user__full_name")
    list_editable = ("status", "priority")
    readonly_fields = ("created_at", "completed_at")

    fieldsets = (
        ("Action", {"fields": ("employee", "title", "description")}),
        ("Priority & Status", {"fields": ("priority", "status", "due_date")}),
        ("Timestamps", {"fields": ("created_at", "completed_at")}),
    )


@admin.register(OnboardingStep)
class OnboardingStepAdmin(admin.ModelAdmin):
    list_display = ("id", "employee", "step_name", "status", "completed_at")
    list_filter = ("step_name", "status", "completed_at")
    search_fields = ("employee__user__full_name",)
    list_editable = ("status",)
    readonly_fields = ("completed_at", "created_at")

    fieldsets = (
        ("Step", {"fields": ("employee", "step_name")}),
        ("Status", {"fields": ("status", "completed_at")}),
        ("Timestamp", {"fields": ("created_at",)}),
    )

