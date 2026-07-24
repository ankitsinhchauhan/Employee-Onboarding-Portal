"""
Dashboard utility functions that delegate to the DashboardService layer.
This module exists for backward compatibility with the class-based views 
in dashboard/views.py.
"""
from employees.models import EmployeeProfile
from employees.services.dashboard_service import DashboardService


def get_employee_profile(user):
    """Get employee profile (backward-compatible wrapper)."""
    return DashboardService.get_employee_profile(user)


def calculate_profile_completion(profile):
    """
    Calculate profile completion (backward-compatible wrapper).
    Accepts a profile object like the old API.
    """
    if not profile:
        return 0
    # If a profile is passed, we use the service with the profile's user
    try:
        employee = DashboardService.get_employee_profile(profile.user)
        return DashboardService.calculate_profile_completion(employee)
    except Exception:
        return 0


def calculate_document_completion(document):
    """
    Calculate document completion (backward-compatible wrapper).
    Old API passed a document - we need the employee.
    """
    try:
        if document and hasattr(document, "employee"):
            return DashboardService.calculate_document_completion(document.employee)
        return 0
    except Exception:
        return 0


def get_verification_status(user, document):
    """Get verification status (backward-compatible wrapper)."""
    try:
        employee = DashboardService.get_employee_profile(user)
        return DashboardService.get_verification_status(employee)
    except Exception:
        return "Not Started"


def get_current_step(profile_completion, document_completion, verification_status):
    """Get current onboarding step (backward-compatible)."""
    return DashboardService.get_current_step(
        profile_completion, document_completion, verification_status
    )


def build_timeline(profile_completion, document_completion, verification_status):
    """Build onboarding timeline (backward-compatible wrapper)."""
    # Employee not available here - build timeline without employee context
    return DashboardService.get_onboarding_timeline(
        None, profile_completion, document_completion, verification_status
    )


def build_required_actions(profile_completion, document_completion):
    """Build required actions (backward-compatible)."""
    return _build_required_actions_helper(profile_completion, document_completion)


def get_user_document(user):
    """Get the user's documents - backward compatible."""
    try:
        profile = EmployeeProfile.objects.get(user=user)
        from employees.models import EmployeeDocument

        return EmployeeDocument.objects.filter(employee=profile).first()
    except (EmployeeProfile.DoesNotExist, AttributeError):
        return None


def _build_required_actions_helper(profile_completion, document_completion):
    """Build required actions list."""
    actions = []
    if document_completion < 100:
        actions.append(
            {
                "title": "Upload documents",
                "description": "Complete pending document uploads",
                "icon": "cloud-upload",
                "button": "Upload Documents",
                "url_name": "dashboard_documents",
            }
        )
    if profile_completion < 100:
        actions.append(
            {
                "title": "Complete profile",
                "description": "Add emergency contact and profile details",
                "icon": "person-check",
                "button": "Complete Profile",
                "url_name": "dashboard_profile",
            }
        )
    actions.append(
        {
            "title": "View approval status",
            "description": "See the latest review progress",
            "icon": "clipboard-check",
            "button": "View Approval Status",
            "url_name": "dashboard_approval_status",
        }
    )
    return actions


def build_document_rows(document):
    """Build document rows for template - backward compatible."""
    DOCUMENT_FIELD_MAP = {
        "RESUME": "Resume / CV",
        "AADHAAR": "Aadhaar Card",
        "PAN": "PAN Card",
        "DEGREE": "Degree Certificate",
        "PHOTO": "Profile Photo",
    }

    rows = []
    for doc_type, label in DOCUMENT_FIELD_MAP.items():
        rows.append(
            {
                "name": label,
                "status": "Not Uploaded",
                "uploaded": "—",
            }
        )
    return rows


def build_approval_timeline(user, profile, document):
    """Build approval timeline - backward compatible."""
    try:
        profile_completion = calculate_profile_completion(profile) or 0
    except Exception:
        profile_completion = 0

    profile_done = profile_completion >= 100

    try:
        document_status = document.verification_status if document else "PENDING"
    except Exception:
        document_status = "PENDING"

    status_map = {
        "PENDING": "Pending",
        "VERIFIED": "Approved",
        "REJECTED": "Rejected",
    }

    display_status = status_map.get(document_status, "Pending")

    return [
        {
            "title": "Offer accepted",
            "status": "completed",
            "date": user.date_joined.strftime("%d %b %Y"),
        },
        {
            "title": "Profile validation",
            "status": "completed" if profile_done else "current",
            "date": "Completed" if profile_done else "In progress",
        },
        {
            "title": "Document review",
            "status": (
                "completed"
                if display_status == "Approved"
                else "current"
                if display_status == "Pending"
                else "pending"
            ),
            "date": document.uploaded_at.strftime("%d %b %Y") if document else "Pending",
        },
        {
            "title": "HR approval",
            "status": "completed" if display_status == "Approved" else "pending",
            "date": "Completed" if display_status == "Approved" else "Pending",
        },
        {
            "title": "Manager approval",
            "status": "completed" if user.status == user.Status.ACTIVE else "pending",
            "date": "Completed" if user.status == user.Status.ACTIVE else "Pending",
        },
    ]