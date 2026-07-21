from django.contrib import admin
from .models import EmployeeProfile

# Register your models here.

admin.site.register(EmployeeProfile)

class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'department', 'designation', 'date_of_joining', 'status')
    search_fields = ('user__full_name')