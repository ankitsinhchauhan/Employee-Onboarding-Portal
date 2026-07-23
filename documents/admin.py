from django.contrib import admin

from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "uploaded_at")
    list_filter = ("status",)
    search_fields = ("user__full_name", "user__personal_email")
