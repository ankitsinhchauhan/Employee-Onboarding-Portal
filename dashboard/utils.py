from documents.models import Document
from employees.models import EmployeeProfile

PROFILE_FIELDS = (
    "department",
    "designation",
    "phone_number",
    "address",
    "date_of_birth",
    "joining_date",
    "emergency_contact",
)

DOCUMENT_FIELDS = (
    ("Resume", "resume"),
    ("Aadhaar Card", "aadhaar_card"),
    ("PAN Card", "pan_card"),
    ("Degree Certificate", "degree_certificate"),
    ("Profile Photo", "passport_photo"),
)


def get_employee_profile(user):
    try:
        return user.employeeprofile
    except EmployeeProfile.DoesNotExist:
        return None


def get_user_document(user):
    return Document.objects.filter(user=user).order_by("-uploaded_at").first()


def calculate_profile_completion(profile):
    if not profile:
        return 0
    filled = sum(1 for field in PROFILE_FIELDS if getattr(profile, field, None))
    return int((filled / len(PROFILE_FIELDS)) * 100)


def calculate_document_completion(document):
    if not document:
        return 0
    filled = sum(1 for _, field in DOCUMENT_FIELDS if getattr(document, field, None))
    return int((filled / len(DOCUMENT_FIELDS)) * 100)


def build_document_rows(document):
    rows = []
    for label, field in DOCUMENT_FIELDS:
        file_field = getattr(document, field, None) if document else None
        if file_field:
            rows.append(
                {
                    "name": label,
                    "status": document.get_status_display(),
                    "uploaded": document.uploaded_at.strftime("%d %b %Y"),
                }
            )
        else:
            rows.append(
                {
                    "name": label,
                    "status": "Pending",
                    "uploaded": "Not uploaded",
                }
            )
    return rows


def get_verification_status(user, document):
    if document:
        return document.get_status_display()
    if user.status == user.Status.ACTIVE:
        return "Approved"
    return "In Review"


def get_current_step(profile_completion, document_completion, verification_status):
    if profile_completion < 100:
        return "Complete Profile"
    if document_completion < 100:
        return "Upload Documents"
    if verification_status == "Pending":
        return "Document Verification"
    if verification_status == "Rejected":
        return "Resubmit Documents"
    if verification_status == "Approved":
        return "Awaiting Final Approval"
    return "Document Verification"


def build_timeline(profile_completion, document_completion, verification_status):
    profile_done = profile_completion >= 100
    documents_done = document_completion >= 100
    review_current = documents_done and verification_status == "Pending"
    review_done = verification_status == "Approved"
    review_rejected = verification_status == "Rejected"

    return [
        {
            "title": "Profile submitted",
            "status": "completed" if profile_done else "current",
            "note": "Employee details received" if profile_done else "Complete your profile details",
        },
        {
            "title": "Documents uploaded",
            "status": "completed" if documents_done else ("current" if profile_done else "pending"),
            "note": "Required files on file" if documents_done else "Upload PAN, Aadhaar, and photo",
        },
        {
            "title": "Document verification",
            "status": (
                "completed"
                if review_done
                else "current"
                if review_current or review_rejected
                else "pending"
            ),
            "note": (
                "HR review completed"
                if review_done
                else "HR review in progress"
                if review_current
                else "Waiting for rejected document resubmission"
                if review_rejected
                else "Waiting for document upload"
            ),
        },
        {
            "title": "Manager approval",
            "status": "completed" if review_done else "pending",
            "note": "Department sign-off received" if review_done else "Waiting for department sign-off",
        },
        {
            "title": "Welcome kit release",
            "status": "completed" if review_done else "pending",
            "note": "Assets and workspace allocation" if review_done else "Pending final approval",
        },
    ]


def build_approval_timeline(user, profile, document):
    profile_done = calculate_profile_completion(profile) >= 100
    document_status = document.get_status_display() if document else "Pending"

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
                if document_status == "Approved"
                else "current"
                if document_status == "Pending"
                else "pending"
            ),
            "date": document.uploaded_at.strftime("%d %b %Y") if document else "Pending",
        },
        {
            "title": "HR approval",
            "status": "completed" if document_status == "Approved" else "pending",
            "date": "Completed" if document_status == "Approved" else "Pending",
        },
        {
            "title": "Manager approval",
            "status": "completed" if user.status == user.Status.ACTIVE else "pending",
            "date": "Completed" if user.status == user.Status.ACTIVE else "Pending",
        },
    ]


def build_required_actions(profile_completion, document_completion):
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
