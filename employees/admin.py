from django.contrib import admin

from .models import EmployeeProfile


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "department",
        "designation",
        "joining_date",
        "phone_number",
    )
    list_filter = ("department",)
    search_fields = ("user__full_name", "user__personal_email", "designation")
