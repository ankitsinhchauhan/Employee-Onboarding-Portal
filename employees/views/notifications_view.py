from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from employees.models import Notification
from employees.services.dashboard_service import DashboardService


@login_required
def notifications_view(request):
    """View all notifications for the employee."""

    employee = DashboardService.get_employee_profile(request.user)
    notifications = DashboardService.get_recent_notifications(employee, limit=50)
    notification_count = DashboardService.get_unread_notification_count(employee)

    context = {
        "notifications": notifications,
        "unread_count": notification_count,
        "employee_name": request.user.full_name,
        "employee_id": employee.employee_id if employee else "Not assigned",
        "department": employee.department if employee else "Not assigned",
        "joining_date": employee.joining_date if employee else request.user.date_joined,
        "profile_completion": DashboardService.calculate_profile_completion(employee),
        "document_completion": DashboardService.calculate_document_completion(employee),
        "verification_status": DashboardService.get_verification_status(employee),
        "overall_status": request.user.get_display_status(),
        "notification_count": notification_count,
        "active_nav": "notifications",
        "page_title": "Notifications",
    }

    return render(request, "dashboard/notifications.html", context)


@login_required
@require_POST
def mark_notification_read(request, notification_id):
    """Mark a single notification as read."""
    try:
        notification = Notification.objects.get(id=notification_id)
        notification.is_read = True
        notification.save()
        return JsonResponse({"status": "ok"})
    except Notification.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Notification not found"}, status=404)


@login_required
@require_POST
def mark_all_notifications_read(request):
    """Mark all notifications as read for the current employee."""
    employee = DashboardService.get_employee_profile(request.user)
    if employee:
        Notification.objects.filter(employee=employee, is_read=False).update(is_read=True)
    return JsonResponse({"status": "ok"})

