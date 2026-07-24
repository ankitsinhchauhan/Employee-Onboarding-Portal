from django.db.models import Count, Q
from django.utils import timezone
from django.db import transaction

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
    "alternate_number",
    "date_of_birth",
    "gender",
    "joining_date",
    "reporting_manager",
    "current_address",
    "permanent_address",
    "city",
    "state",
    "country",
    "pincode",
    "emergency_contact_name",
    "emergency_contact_phone",
    "emergency_contact_relationship",
]

DOCUMENT_FIELD_MAP = {
    "RESUME": "Resume / CV",
    "AADHAAR": "Aadhaar Card",
    "PAN": "PAN Card",
    "PHOTO": "Passport Photo",
    "DEGREE": "Degree Certificate",
    "EXPERIENCE": "Experience Letter",
    "OFFER_LETTER": "Offer Letter",
}

REQUIRED_DOCUMENT_TYPES = ["AADHAAR", "PAN", "PHOTO", "DEGREE"]


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

        # Also check profile_picture
        if profile.profile_picture:
            filled += 1
            total_fields = len(PROFILE_FIELDS) + 1
        else:
            total_fields = len(PROFILE_FIELDS)

        percentage = int((filled / total_fields) * 100)
        return min(percentage, 100)

    @staticmethod
    def calculate_document_completion(employee):
        """
        Calculate document completion percentage.
        Based on how many of the required document types have been uploaded.
        Returns an integer between 0 and 100.
        """
        required_types = REQUIRED_DOCUMENT_TYPES
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
    def calculate_overall_progress(profile):
        """
        Calculate overall onboarding progress based on profile and documents.
        """
        if not profile:
            return 0

        profile_completion = DashboardService.calculate_profile_completion(profile)
        document_completion = DashboardService.calculate_document_completion(profile)

        # Weight: 40% profile, 60% documents
        overall = int((profile_completion * 0.4) + (document_completion * 0.6))
        return min(overall, 100)

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

        all_verified_count = documents.filter(verification_status="VERIFIED").count()
        total = documents.count()

        if all_verified_count == total and total > 0:
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

        # Auto-create actions based on profile/document status
        DashboardService._auto_create_required_actions(employee)

        return RequiredAction.objects.filter(
            employee=employee, status__in=["PENDING", "OVERDUE"]
        ).order_by("due_date", "created_at")[:limit]

    @staticmethod
    def _auto_create_required_actions(employee):
        """Auto-create required actions based on incomplete tasks."""
        if not employee:
            return

        profile_completion = DashboardService.calculate_profile_completion(employee)
        document_completion = DashboardService.calculate_document_completion(employee)

        actions_to_create = []

        if profile_completion < 100:
            if not RequiredAction.objects.filter(
                employee=employee,
                title__icontains="Complete your profile",
                status="PENDING",
            ).exists():
                actions_to_create.append(
                    RequiredAction(
                        employee=employee,
                        title="Complete your profile",
                        description="Add your personal details, address, emergency contact, and profile picture.",
                        priority="HIGH",
                        status="PENDING",
                    )
                )

        if document_completion < 100:
            missing_docs = DashboardService._get_missing_required_documents(employee)
            if missing_docs:
                doc_names = ", ".join(missing_docs)
                if not RequiredAction.objects.filter(
                    employee=employee,
                    title__icontains="Upload required documents",
                    status="PENDING",
                ).exists():
                    actions_to_create.append(
                        RequiredAction(
                            employee=employee,
                            title="Upload required documents",
                            description=f"Upload the following documents: {doc_names}",
                            priority="HIGH",
                            status="PENDING",
                        )
                    )

        if actions_to_create:
            RequiredAction.objects.bulk_create(actions_to_create)

    @staticmethod
    def _get_missing_required_documents(employee):
        """Get list of missing required document type labels."""
        uploaded_types = set(
            EmployeeDocument.objects.filter(
                employee=employee, document_type__in=REQUIRED_DOCUMENT_TYPES
            ).values_list("document_type", flat=True)
        )
        missing = []
        for doc_type in REQUIRED_DOCUMENT_TYPES:
            if doc_type not in uploaded_types:
                missing.append(dict(EmployeeDocument.DOCUMENT_TYPES).get(doc_type, doc_type))
        return missing

    @staticmethod
    def get_recent_notifications(employee, limit=10, category=None):
        """
        Get recent notifications for an employee.
        Optionally filter by category.
        """
        if not employee:
            return Notification.objects.none()

        queryset = Notification.objects.filter(employee=employee)
        if category:
            queryset = queryset.filter(category=category)
        return queryset.order_by("-created_at")[:limit]

    @staticmethod
    def get_notifications_paginated(employee, page=1, per_page=10, category=None, search=None):
        """Get paginated notifications with optional filtering."""
        from django.core.paginator import EmptyPage, Paginator

        if not employee:
            return {"notifications": [], "page": 1, "total_pages": 1, "total": 0}

        queryset = Notification.objects.filter(employee=employee)

        if category and category != "ALL":
            queryset = queryset.filter(category=category)

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(message__icontains=search)
            )

        queryset = queryset.order_by("-created_at")
        paginator = Paginator(queryset, per_page)

        try:
            page_obj = paginator.page(page)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        return {
            "notifications": page_obj.object_list,
            "page": page_obj.number,
            "total_pages": paginator.num_pages,
            "total": paginator.count,
            "has_next": page_obj.has_next(),
            "has_previous": page_obj.has_previous(),
        }

    @staticmethod
    def get_unread_notification_count(employee):
        """Get count of unread notifications."""
        if not employee:
            return 0
        return Notification.objects.filter(employee=employee, is_read=False).count()

    @staticmethod
    def get_notification_category_counts(employee):
        """Get notification counts by category."""
        if not employee:
            return {}
        counts = {}
        for cat_key, cat_label in Notification.CATEGORY_CHOICES:
            counts[cat_key] = Notification.objects.filter(
                employee=employee, category=cat_key
            ).count()
        return counts

    @staticmethod
    def create_notification(employee, title, message="", category="SYSTEM"):
        """Create a notification for an employee."""
        if not employee:
            return None
        return Notification.objects.create(
            employee=employee,
            title=title,
            message=message,
            category=category,
        )

    @staticmethod
    def get_onboarding_progress(employee):
        """
        Calculate overall onboarding progress based on steps.
        Returns a dict with step info and overall percentage.
        """
        if not employee:
            return {"overall": 0, "steps": [], "completed_steps": 0, "total_steps": 0}

        steps = OnboardingStep.objects.filter(employee=employee).order_by("created_at")

        if not steps.exists():
            # Create default onboarding steps
            step_names = [
                "PROFILE_COMPLETION",
                "DOCUMENT_UPLOAD",
                "DOCUMENT_VERIFICATION",
                "HR_APPROVAL",
                "MANAGER_APPROVAL",
                "ADMIN_APPROVAL",
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

        # Auto-update step statuses based on actual progress
        DashboardService._auto_update_step_statuses(employee, steps)

        # Refresh steps after auto-update
        steps = OnboardingStep.objects.filter(employee=employee).order_by("created_at")
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
    def _auto_update_step_statuses(employee, steps):
        """Update onboarding step statuses based on actual progress."""
        profile_completion = DashboardService.calculate_profile_completion(employee)
        document_completion = DashboardService.calculate_document_completion(employee)
        verification_status = DashboardService.get_verification_status(employee)

        updates = {}

        # Step 1: Profile Completion
        if profile_completion >= 100:
            updates["PROFILE_COMPLETION"] = "COMPLETED"
        elif profile_completion > 0:
            updates["PROFILE_COMPLETION"] = "IN_PROGRESS"

        # Step 2: Document Upload
        if document_completion >= 100:
            updates["DOCUMENT_UPLOAD"] = "COMPLETED"
        elif document_completion > 0:
            updates["DOCUMENT_UPLOAD"] = "IN_PROGRESS"

        # Step 3: Document Verification
        if verification_status == "Verified":
            updates["DOCUMENT_VERIFICATION"] = "COMPLETED"
        elif verification_status in ("Pending", "Rejected"):
            updates["DOCUMENT_VERIFICATION"] = "IN_PROGRESS"

        # Step 4-6: Approvals
        if verification_status == "Verified":
            updates["HR_APPROVAL"] = "IN_PROGRESS"

        # Apply updates
        for step in steps:
            if step.step_name in updates:
                new_status = updates[step.step_name]
                if step.status != new_status:
                    step.status = new_status
                    if new_status == "COMPLETED" and not step.completed_at:
                        step.completed_at = timezone.now()
                    step.save()

    @staticmethod
    def get_dashboard_statistics(employee):
        """
        Get comprehensive dashboard statistics.
        """
        if not employee:
            return {
                "profile_completion": 0,
                "document_completion": 0,
                "overall_progress": 0,
                "verification_status": "Not Started",
                "total_documents": 0,
                "verified_documents": 0,
                "rejected_documents": 0,
                "pending_documents": 0,
                "pending_actions_count": 0,
                "unread_notifications": 0,
                "onboarding_progress": 0,
            }

        documents = EmployeeDocument.objects.filter(employee=employee)
        total_doc_count = documents.count()
        verified_doc_count = documents.filter(verification_status="VERIFIED").count()
        rejected_doc_count = documents.filter(verification_status="REJECTED").count()
        pending_doc_count = documents.filter(verification_status="PENDING").count()

        profile_completion = DashboardService.calculate_profile_completion(employee)
        document_completion = DashboardService.calculate_document_completion(employee)
        overall_progress = DashboardService.calculate_overall_progress(employee)
        verification_status = DashboardService.get_verification_status(employee)
        onboarding = DashboardService.get_onboarding_progress(employee)

        return {
            "profile_completion": profile_completion,
            "document_completion": document_completion,
            "overall_progress": overall_progress,
            "verification_status": verification_status,
            "total_documents": total_doc_count,
            "verified_documents": verified_doc_count,
            "rejected_documents": rejected_doc_count,
            "pending_documents": pending_doc_count,
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
        Uses OnboardingStep model for status, falls back to computed values.
        """
        # Try to get from DB first
        if employee:
            steps = OnboardingStep.objects.filter(employee=employee).order_by("created_at")
            if steps.exists():
                return DashboardService._build_timeline_from_steps(steps)

        # Fallback to computed timeline
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
                "title": "HR Approval",
                "status": "completed" if review_done else ("current" if review_done else "pending"),
                "note": "HR review completed" if review_done else "Pending HR review",
            },
            {
                "title": "Manager Approval",
                "status": "completed" if review_done else "pending",
                "note": "Department sign-off received" if review_done else "Waiting for department sign-off",
            },
            {
                "title": "Admin Approval",
                "status": "completed" if review_done else "pending",
                "note": "Final approval pending" if not review_done else "All approvals completed",
            },
        ]

    @staticmethod
    def _build_timeline_from_steps(steps):
        """Build timeline data from OnboardingStep model instances."""
        display_map = dict(OnboardingStep.STEP_CHOICES)
        timeline = []
        for step in steps:
            status = step.status.lower()
            if status == "in_progress":
                status = "current"
            timeline.append({
                "title": display_map.get(step.step_name, step.step_name),
                "status": status,
                "note": DashboardService._get_step_note(step),
                "date": step.completed_at.strftime("%d %b %Y") if step.completed_at else None,
            })
        return timeline

    @staticmethod
    def _get_step_note(step):
        """Get contextual note for an onboarding step."""
        notes = {
            "PROFILE_COMPLETION": {
                "COMPLETED": "Profile details submitted successfully",
                "IN_PROGRESS": "Complete your profile details",
                "PENDING": "Start filling in your profile",
            },
            "DOCUMENT_UPLOAD": {
                "COMPLETED": "All required documents uploaded",
                "IN_PROGRESS": "Upload remaining documents",
                "PENDING": "Documents pending upload",
            },
            "DOCUMENT_VERIFICATION": {
                "COMPLETED": "Documents verified by HR",
                "IN_PROGRESS": "HR reviewing documents",
                "PENDING": "Awaiting document upload",
            },
            "HR_APPROVAL": {
                "COMPLETED": "HR approval completed",
                "IN_PROGRESS": "HR review in progress",
                "PENDING": "Pending HR review",
            },
            "MANAGER_APPROVAL": {
                "COMPLETED": "Manager signed off",
                "IN_PROGRESS": "Manager review in progress",
                "PENDING": "Pending manager approval",
            },
            "ADMIN_APPROVAL": {
                "COMPLETED": "All approvals completed",
                "IN_PROGRESS": "Admin review in progress",
                "PENDING": "Pending final approval",
            },
            "COMPLETED": {
                "COMPLETED": "Onboarding process completed successfully",
                "PENDING": "Onboarding process not yet completed",
            },
        }
        step_notes = notes.get(step.step_name, {})
        return step_notes.get(step.status, f"Status: {step.get_status_display()}")

    @staticmethod
    def get_dashboard_summary(user):
        """
        Get comprehensive dashboard summary for the authenticated user.
        """
        employee = DashboardService.get_employee_profile(user)

        if not employee:
            return {
                "employee": None,
                "error": "Employee profile not found. Please contact HR.",
            }

        profile_completion = DashboardService.calculate_profile_completion(employee)
        document_completion = DashboardService.calculate_document_completion(employee)
        overall_progress = DashboardService.calculate_overall_progress(employee)
        verification_status = DashboardService.get_verification_status(employee)

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

    @staticmethod
    def update_onboarding_steps(employee):
        """Trigger step status updates. Called when profile/document changes."""
        DashboardService._auto_update_step_statuses(
            employee,
            OnboardingStep.objects.filter(employee=employee)
        )

