from django.contrib import admin
from .models import User

# Register your models here.

admin.site.register(User)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'personal_email', 'company_email', 'role', 'status')
    list_filter = ('role', 'status')
    serarch_fields = ('full_name', 'personal_email')


