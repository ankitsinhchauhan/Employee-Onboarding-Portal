from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from employees.services.dashboard_service import DashboardService


@login_required
def required_actions_view(request):
    """
    Required Actions page.
    
    NOTE: This page overlaps significantly with Dashboard pending tasks.
    Recommendation: Keep this as a detailed view of pending actions.
    The Dashboard already shows a summary of pending actions.
    This page provides more detail and filtering.
    """

    employee = DashboardService.get_employee_profile(request.user)
    
    if not employee:
        return redirect("dashboard")

    # Get all pending actions (no limit for this page)
    actions = DashboardService.get_pending_actions(employee, limit=50)
    notification_count = DashboardService.get_unread_notification_count(employee)

    # Build action cards for template
    action_list = [
        {
            "title": action.title,
            "description": action.description or "Complete this action to proceed with onboarding.",
            "priority": action.priority,
            "priority_label": action.get_priority_display(),
            "icon": "exclamation-circle" if action.priority in ("HIGH", "URGENT") else "clipboard-check",
            "button": "Complete Now",
            "url_name": _get_action_url(action.title),
            "status": action.get_status_display(),
            "due_date": action.due_date.strftime("%d %b %Y") if action.due_date else None,
        }
        for action in actions
    ]

    # Add default suggestions if no actions exist
    if not action_list:
        profile_completion = DashboardService.calculate_profile_completion(employee)
        document_completion = DashboardService.calculate_document_completion(employee)

        if profile_completion < 100:
            action_list.append(
                {
                    "title": "Complete your profile",
                    "description": "Add your contact details, emergency contact, and other required information.",
                    "priority": "HIGH",
                    "priority_label": "High",
                    "icon": "person-check",
                    "button": "Complete Profile",
                    "url_name": "dashboard_profile",
                    "status": "Pending",
                    "due_date": None,
                }
            )
        if document_completion < 100:
            action_list.append(
                {
                    "title": "Upload required documents",
                    "description": "Upload your PAN card, Aadhaar card, degree certificate, and profile photo.",
                    "priority": "HIGH",
                    "priority_label": "High",
                    "icon": "cloud-upload",
                    "button": "Upload Documents",
                    "url_name": "dashboard_documents",
                    "status": "Pending",
                    "due_date": None,
                }
            )

        action_list.append(
            {
                "title": "Check approval status",
                "description": "Track the progress of your document verification and approvals.",
                "priority": "MEDIUM",
                "priority_label": "Medium",
                "icon": "diagram-3",
                "button": "View Status",
                "url_name": "dashboard_approval_status",
                "status": "Info",
                "due_date": None,
            }
        )

    profile_completion = DashboardService.calculate_profile_completion(employee)
    document_completion = DashboardService.calculate_document_completion(employee)

    context = {
        "actions": action_list,
        "employee_name": request.user.full_name,
        "employee_id": employee.employee_id,
        "department": employee.department or "Not assigned",
        "designation": employee.designation or "Not assigned",
        "joining_date": employee.joining_date if employee.joining_date else request.user.date_joined,
        "profile_completion": profile_completion,
        "document_completion": document_completion,
        "verification_status": DashboardService.get_verification_status(employee),
        "overall_progress": DashboardService.calculate_overall_progress(employee),
        "overall_status": request.user.get_display_status(),
        "notification_count": notification_count,
        "active_nav": "required_actions",
        "page_title": "Required Actions",
    }

    return render(request, "dashboard/required_actions.html", context)


def _get_action_url(title):
    """Map action title to URL name."""
    title_lower = title.lower()
    if "profile" in title_lower:
        return "dashboard_profile"
    if "document" in title_lower or "upload" in title_lower:
        return "dashboard_documents"
    if "approval" in title_lower or "status" in title_lower:
        return "dashboard_approval_status"
    return "dashboard"

