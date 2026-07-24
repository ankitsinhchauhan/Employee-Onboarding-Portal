from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from employees.models import Notification
from employees.services.dashboard_service import DashboardService


@login_required
def notifications_view(request):
    """View all notifications with pagination, filtering, and search."""

    employee = DashboardService.get_employee_profile(request.user)
    
    if not employee:
        context = {
            "employee_name": request.user.full_name,
            "employee_id": "Not assigned",
            "error": "Employee profile not found",
            "active_nav": "notifications",
            "page_title": "Notifications",
        }
        return render(request, "dashboard/notifications.html", context)

    # Get filter parameters
    page = int(request.GET.get("page", 1))
    category = request.GET.get("category", "ALL")
    search_query = request.GET.get("search", "").strip()

    # Get paginated notifications
    notification_data = DashboardService.get_notifications_paginated(
        employee, page=page, per_page=10, category=category, search=search_query
    )

    notifications = notification_data["notifications"]
    
    # Get category counts
    category_counts = DashboardService.get_notification_category_counts(employee)
    total_notifications = sum(category_counts.values())

    profile_completion = DashboardService.calculate_profile_completion(employee)
    document_completion = DashboardService.calculate_document_completion(employee)
    verification_status = DashboardService.get_verification_status(employee)
    notification_count = DashboardService.get_unread_notification_count(employee)

    # Build notification items for template
    notification_items = []
    for notif in notifications:
        notification_items.append({
            "id": notif.id,
            "title": notif.title,
            "message": notif.message or "",
            "category": notif.category,
            "category_label": notif.get_category_display(),
            "is_read": notif.is_read,
            "created_at": notif.created_at,
            "created_at_display": _format_notification_time(notif.created_at),
        })

    context = {
        "notifications": notification_items,
        "unread_count": notification_count,
        "total_count": total_notifications,
        "category_counts": category_counts,
        "current_category": category,
        "search_query": search_query,
        "current_page": notification_data["page"],
        "total_pages": notification_data["total_pages"],
        "total_notifications": notification_data["total"],
        "has_next": notification_data["has_next"],
        "has_previous": notification_data["has_previous"],
        "employee": employee,
        "employee_name": request.user.full_name,
        "employee_id": employee.employee_id if employee else "Not assigned",
        "department": employee.department if employee else "Not assigned",
        "designation": employee.designation or "Not assigned",
        "joining_date": employee.joining_date if employee else request.user.date_joined,
        "profile_completion": profile_completion,
        "document_completion": document_completion,
        "verification_status": verification_status,
        "overall_progress": DashboardService.calculate_overall_progress(employee),
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
        notification = Notification.objects.get(id=notification_id, employee__user=request.user)
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
        # Optionally filter by category
        category = request.POST.get("category")
        queryset = Notification.objects.filter(employee=employee, is_read=False)
        if category:
            queryset = queryset.filter(category=category)
        queryset.update(is_read=True)
    return JsonResponse({"status": "ok"})


def _format_notification_time(dt):
    """Format notification time for display."""
    from django.utils import timezone
    now = timezone.now()
    diff = now - dt

    if diff.days == 0:
        if diff.seconds < 60:
            return "Just now"
        elif diff.seconds < 3600:
            mins = diff.seconds // 60
            return f"{mins} min{'s' if mins != 1 else ''} ago"
        else:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.days == 1:
        return "Yesterday"
    elif diff.days < 7:
        return f"{diff.days} days ago"
    elif diff.days < 30:
        weeks = diff.days // 7
        return f"{weeks} week{'s' if weeks != 1 else ''} ago"
    else:
        return dt.strftime("%d %b %Y, %I:%M %p")

