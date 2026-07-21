from django.contrib import admin
from .models import Document

# Register your models here.

admin.site.register(Document)
@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'uploaded_at')
    list_filter = ('status')