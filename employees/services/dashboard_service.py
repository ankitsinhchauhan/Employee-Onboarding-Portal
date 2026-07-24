from django.db.models import Count, Q
from django.utils import timezone

from employees.models import (
    EmployeeDocument,
    EmployeeProfile,
    Notification,
    OnboardingStep,
    RequiredAction,
)

PROFILE_FIELDS = [
    "department",
    "designation",
    "phone_number",
    "address",
    "date_of_birth",
    "joining_date",
    "emergency_contact_name",
    "emergency_contact_phone",
]

DOCUMENT_FIELD_MAP = {
    "RESUME": "Resume / CV",
    "AADHAAR": "Aadhaar Card",
    "PAN": "PAN Card",
    "DEGREE": "Degree Certificate",
    "PHOTO": "Profile Photo",
}


class DashboardService:

    @staticmethod
    def get_employee_profile(user):
        """Get or create an employee profile for the user."""
        try:
            profile, created = EmployeeProfile.objects.get_or_create(
                user=user,
                defaults={"employee_id": f"EMP-{user.id:06d}"},
            )
            return profile
        except EmployeeProfile.DoesNotExist:
            return None

    @staticmethod
    def get_employee_documents(employee):
        """Get all documents for an employee."""
        return EmployeeDocument.objects.filter(employee=employee)

    @staticmethod
    def calculate_profile_completion(profile):
        """
        Calculate profile completion percentage based on filled fields.
        Returns an integer between 0 and 100.
        """
        if not profile:
            return 0

        filled = 0
        for field in PROFILE_FIELDS:
            value = getattr(profile, field, None)
            if value is not None and str(value).strip():
                filled += 1

        percentage = int((filled / len(PROFILE_FIELDS)) * 100)
        return min(percentage, 100)

    @staticmethod
    def calculate_document_completion(employee):
        """
        Calculate document completion percentage.
        Based on how many of the required document types have been uploaded.
        Returns an integer between 0 and 100.
        """
        required_types = list(DOCUMENT_FIELD_MAP.keys())
        uploaded_types = (
            EmployeeDocument.objects.filter(
                employee=employee, document_type__in=required_types
            )
            .values_list("document_type", flat=True)
            .distinct()
        )

        uploaded_count = len(set(uploaded_types))
        required_count = len(required_types)

        if required_count == 0:
            return 0

        return int((uploaded_count / required_count) * 100)

    @staticmethod
    def get_verification_status(employee):
        """
        Get the overall verification status based on documents.
        Returns one of: 'Pending', 'Verified', 'Rejected', 'Not Started'.
        """
        if not employee:
            return "Not Started"

        documents = EmployeeDocument.objects.filter(employee=employee)

        if not documents.exists():
            return "Not Started"

        if documents.filter(verification_status="REJECTED").exists():
            return "Rejected"

        all_verified = documents.filter(verification_status="VERIFIED").count()
        total = documents.count()

        if all_verified == total and total > 0:
            return "Verified"

        if documents.filter(verification_status="PENDING").exists():
            return "Pending"

        return "Pending"

    @staticmethod
    def get_pending_actions(employee, limit=5):
        """
        Get pending required actions for an employee.
        """
        if not employee:
            return RequiredAction.objects.none()

        return RequiredAction.objects.filter(
            employee=employee, status__in=["PENDING", "OVERDUE"]
        ).order_by("due_date", "created_at")[:limit]

    @staticmethod
    def get_recent_notifications(employee, limit=5):
        """
        Get recent notifications for an employee.
        """
        if not employee:
            return Notification.objects.none()

        return Notification.objects.filter(employee=employee).order_by("-created_at")[
            :limit
        ]

    @staticmethod
    def get_unread_notification_count(employee):
        """Get count of unread notifications."""
        if not employee:
            return 0
        return Notification.objects.filter(employee=employee, is_read=False).count()

    @staticmethod
    def get_onboarding_progress(employee):
        """
        Calculate overall onboarding progress based on steps.
        Returns a dict with step info and overall percentage.
        """
        if not employee:
            return {"overall": 0, "steps": []}

        steps = OnboardingStep.objects.filter(employee=employee).order_by("created_at")

        if not steps.exists():
            # Create default onboarding steps
            step_names = [
                "PROFILE_COMPLETION",
                "DOCUMENT_UPLOAD",
                "DOCUMENT_VERIFICATION",
                "HR_APPROVAL",
                "MANAGER_APPROVAL",
                "WELCOME_KIT",
            ]
            for idx, step_name in enumerate(step_names):
                OnboardingStep.objects.create(
                    employee=employee,
                    step_name=step_name,
                    status="COMPLETED" if idx == 0 else "PENDING",
                )
            steps = OnboardingStep.objects.filter(employee=employee).order_by(
                "created_at"
            )

        completed_steps = steps.filter(status="COMPLETED").count()
        total_steps = steps.count()

        overall = int((completed_steps / max(total_steps, 1)) * 100)

        return {
            "overall": overall,
            "steps": steps,
            "completed_steps": completed_steps,
            "total_steps": total_steps,
        }

    @staticmethod
    def get_dashboard_statistics(employee):
        """
        Get comprehensive dashboard statistics.
        """
        if not employee:
            return {
                "profile_completion": 0,
                "document_completion": 0,
                "verification_status": "Not Started",
                "total_documents": 0,
                "verified_documents": 0,
                "pending_actions_count": 0,
                "unread_notifications": 0,
                "onboarding_progress": 0,
            }

        documents = EmployeeDocument.objects.filter(employee=employee)
        total_doc_count = documents.count()
        verified_doc_count = documents.filter(verification_status="VERIFIED").count()

        profile_completion = DashboardService.calculate_profile_completion(employee)
        document_completion = DashboardService.calculate_document_completion(employee)
        verification_status = DashboardService.get_verification_status(employee)
        onboarding = DashboardService.get_onboarding_progress(employee)

        return {
            "profile_completion": profile_completion,
            "document_completion": document_completion,
            "verification_status": verification_status,
            "total_documents": total_doc_count,
            "verified_documents": verified_doc_count,
            "pending_actions_count": RequiredAction.objects.filter(
                employee=employee, status__in=["PENDING", "OVERDUE"]
            ).count(),
            "unread_notifications": Notification.objects.filter(
                employee=employee, is_read=False
            ).count(),
            "onboarding_progress": onboarding["overall"],
        }

    @staticmethod
    def get_onboarding_timeline(employee, profile_completion, document_completion, verification_status):
        """
        Build onboarding timeline steps with their statuses.
        """
        profile_done = profile_completion >= 100
        docs_done = document_completion >= 100
        review_current = docs_done and verification_status == "Pending"
        review_done = verification_status == "Verified"
        review_rejected = verification_status == "Rejected"

        return [
            {
                "title": "Profile Submitted",
                "status": "completed" if profile_done else "current" if not docs_done else "pending",
                "note": "Employee details received" if profile_done else "Complete your profile details",
            },
            {
                "title": "Documents Uploaded",
                "status": "completed" if docs_done else ("current" if profile_done else "pending"),
                "note": "Required files on file" if docs_done else "Upload PAN, Aadhaar, and photo",
            },
            {
                "title": "Document Verification",
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
                "title": "Manager Approval",
                "status": "completed" if review_done else "pending",
                "note": "Department sign-off received" if review_done else "Waiting for department sign-off",
            },
            {
                "title": "Welcome Kit Release",
                "status": "completed" if review_done else "pending",
                "note": "Assets and workspace allocation" if review_done else "Pending final approval",
            },
        ]

    @staticmethod
    def get_dashboard_data(user):
        """
        Get all dashboard data for the authenticated user.
        This is the main entry point for the dashboard view.
        """
        employee = DashboardService.get_employee_profile(user)

        if not employee:
            return {
                "employee": None,
                "error": "Employee profile not found. Please contact HR.",
                "active_nav": "dashboard",
            }

        profile_completion = DashboardService.calculate_profile_completion(employee)
        document_completion = DashboardService.calculate_document_completion(employee)
        verification_status = DashboardService.get_verification_status(employee)
        overall_progress = int((profile_completion + document_completion) / 2)

        # Update profile completion percentage in DB
        if employee.profile_completion_percentage != profile_completion:
            EmployeeProfile.objects.filter(pk=employee.pk).update(
                profile_completion_percentage=profile_completion,
                profile_completed=(profile_completion >= 100),
            )
            employee.refresh_from_db()

        notifications = DashboardService.get_recent_notifications(employee)
        actions = DashboardService.get_pending_actions(employee)
        stats = DashboardService.get_dashboard_statistics(employee)
        timeline = DashboardService.get_onboarding_timeline(
            employee, profile_completion, document_completion, verification_status
        )

        return {
            "employee": employee,
            "employee_name": user.full_name,
            "employee_id": employee.employee_id,
            "department": employee.department or "Not Assigned",
            "designation": employee.designation or "Not Assigned",
            "joining_date": employee.joining_date or user.date_joined,
            "profile_completion": profile_completion,
            "document_completion": document_completion,
            "verification_status": verification_status,
            "overall_progress": overall_progress,
            "overall_status": user.get_display_status(),
            "current_step": DashboardService.get_current_step(
                profile_completion, document_completion, verification_status
            ),
            "notifications": notifications,
            "actions": actions,
            "stats": stats,
            "timeline_steps": timeline,
            "notification_count": DashboardService.get_unread_notification_count(employee),
            "active_nav": "dashboard",
        }

    @staticmethod
    def get_current_step(profile_completion, document_completion, verification_status):
        """Determine the current onboarding step based on progress."""
        if profile_completion < 100:
            return "Complete Profile"
        if document_completion < 100:
            return "Upload Documents"
        if verification_status in ("Pending", "Not Started"):
            return "Document Verification"
        if verification_status == "Rejected":
            return "Resubmit Documents"
        if verification_status == "Verified":
            return "Awaiting Final Approval"
        return "Document Verification"

