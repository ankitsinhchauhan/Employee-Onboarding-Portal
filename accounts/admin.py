from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ("personal_email",)
    list_display = (
        "id",
        "full_name",
        "personal_email",
        "company_email",
        "role",
        "status",
        "is_active",
        "date_joined",
    )
    list_filter = ("role", "status", "is_active", "is_staff")
    search_fields = ("full_name", "personal_email", "company_email", "employee_id")

    fieldsets = (
        (None, {"fields": ("personal_email", "password")}),
        ("Personal info", {"fields": ("full_name", "company_email", "employee_id", "hr_id")}),
        ("Access", {"fields": ("role", "status", "is_first_login")}),
        (
            "Permissions",
            {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")},
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "personal_email",
                    "full_name",
                    "password1",
                    "password2",
                    "role",
                    "status",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )
