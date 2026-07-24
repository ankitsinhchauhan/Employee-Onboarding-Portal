from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from employees.services.dashboard_service import DashboardService


@login_required
def required_actions_view(request):
    """View all pending required actions."""

    employee = DashboardService.get_employee_profile(request.user)
    actions = DashboardService.get_pending_actions(employee, limit=50)
    notification_count = DashboardService.get_unread_notification_count(employee)

    # Build action cards for template
    action_list = [
        {
            "title": action.title,
            "description": action.description or "Complete this action to proceed with onboarding.",
            "icon": "clipboard-check",
            "button": "Complete",
            "url_name": "dashboard_documents",
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
                "icon": "diagram-3",
                "button": "View Status",
                "url_name": "dashboard_approval_status",
                "status": "Info",
                "due_date": None,
            }
        )

    context = {
        "actions": action_list,
        "employee_name": request.user.full_name,
        "employee_id": employee.employee_id if employee else "Not assigned",
        "department": employee.department if employee else "Not assigned",
        "joining_date": employee.joining_date if employee else request.user.date_joined,
        "profile_completion": DashboardService.calculate_profile_completion(employee),
        "document_completion": DashboardService.calculate_document_completion(employee),
        "verification_status": DashboardService.get_verification_status(employee),
        "overall_status": request.user.get_display_status(),
        "notification_count": notification_count,
        "active_nav": "required_actions",
        "page_title": "Required Actions",
    }

    return render(request, "dashboard/required_actions.html", context)

