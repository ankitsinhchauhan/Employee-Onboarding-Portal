from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from employees.services.dashboard_service import DashboardService


@login_required
def settings_view(request):
    """View for employee notification and account settings."""

    employee = DashboardService.get_employee_profile(request.user)
    notification_count = DashboardService.get_unread_notification_count(employee)

    context = {
        "settings": [
            {
                "label": "Email notifications",
                "description": "Receive onboarding status updates via email.",
                "enabled": True,
            },
            {
                "label": "Document reminders",
                "description": "Get reminded when documents are pending or rejected.",
                "enabled": True,
            },
            {
                "label": "Weekly summary",
                "description": "Receive a weekly digest of your onboarding progress.",
                "enabled": False,
            },
            {
                "label": "Profile updates",
                "description": "Notifications when your profile is reviewed by HR.",
                "enabled": True,
            },
        ],
        "employee_name": request.user.full_name,
        "employee_id": employee.employee_id if employee else "Not assigned",
        "department": employee.department if employee else "Not assigned",
        "joining_date": employee.joining_date if employee else request.user.date_joined,
        "profile_completion": DashboardService.calculate_profile_completion(employee),
        "document_completion": DashboardService.calculate_document_completion(employee),
        "verification_status": DashboardService.get_verification_status(employee),
        "overall_status": request.user.get_display_status(),
        "notification_count": notification_count,
        "active_nav": "settings",
        "page_title": "Settings",
    }

    return render(request, "dashboard/settings.html", context)

