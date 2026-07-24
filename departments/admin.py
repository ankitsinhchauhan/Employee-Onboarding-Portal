from django.contrib import admin

from .models import Department


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "code", "description")
    search_fields = ("name", "code")
    list_filter = ("name",)

