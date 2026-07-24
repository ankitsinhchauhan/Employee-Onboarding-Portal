from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from employees.models import OnboardingStep
from employees.services.dashboard_service import DashboardService


@login_required
def approval_status_view(request):
    """View onboarding approval status with dynamic timeline from database."""

    employee = DashboardService.get_employee_profile(request.user)
    
    if not employee:
        return redirect("dashboard")

    profile_completion = DashboardService.calculate_profile_completion(employee)
    document_completion = DashboardService.calculate_document_completion(employee)
    verification_status = DashboardService.get_verification_status(employee)
    notification_count = DashboardService.get_unread_notification_count(employee)

    # Get onboarding progress from DB
    onboarding = DashboardService.get_onboarding_progress(employee)
    
    # Build timeline from steps
    timeline_items = []
    for step in onboarding["steps"]:
        status_class = step.status.lower()
        if status_class == "in_progress":
            status_class = "current"
        
        timeline_items.append({
            "step_name": step.get_step_name_display(),
            "status": status_class,
            "status_label": step.get_status_display(),
            "completed_at": step.completed_at.strftime("%d %b %Y, %I:%M %p") if step.completed_at else None,
            "date_display": step.completed_at.strftime("%d %b %Y") if step.completed_at else "Pending",
        })

    # Calculate timeline percentages
    total_steps = onboarding["total_steps"]
    completed_steps = onboarding["completed_steps"]
    progress_percentage = onboarding["overall"]

    context = {
        "employee": employee,
        "timeline_items": timeline_items,
        "total_steps": total_steps,
        "completed_steps": completed_steps,
        "progress_percentage": progress_percentage,
        "profile_completion": profile_completion,
        "document_completion": document_completion,
        "verification_status": verification_status,
        "verification_status_label": verification_status,
        "overall_progress": DashboardService.calculate_overall_progress(employee),
        "employee_name": request.user.full_name,
        "employee_id": employee.employee_id,
        "department": employee.department or "Not assigned",
        "designation": employee.designation or "Not assigned",
        "joining_date": employee.joining_date if employee.joining_date else request.user.date_joined,
        "overall_status": request.user.get_display_status(),
        "notification_count": notification_count,
        "active_nav": "approval_status",
        "page_title": "Approval Status",
    }

    return render(request, "dashboard/approval_status.html", context)

