from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from .utils import (
    build_approval_timeline,
    build_document_rows,
    build_required_actions,
    build_timeline,
    calculate_document_completion,
    calculate_profile_completion,
    get_current_step,
    get_employee_profile,
    get_user_document,
    get_verification_status,
)


def _value(source, attribute, fallback):
    if source is None:
        return fallback
    value = getattr(source, attribute, None)
    if value in (None, ""):
        return fallback
    return value


class DashboardContextMixin:
    page_title = "Dashboard"
    active_nav = "dashboard"

    def get_onboarding_state(self):
        user = self.request.user
        profile = get_employee_profile(user)
        document = get_user_document(user)
        profile_completion = calculate_profile_completion(profile)
        document_completion = calculate_document_completion(document)
        verification_status = get_verification_status(user, document)
        overall_progress = int((profile_completion + document_completion) / 2)

        return {
            "profile": profile,
            "document": document,
            "profile_completion": profile_completion,
            "document_completion": document_completion,
            "verification_status": verification_status,
            "overall_progress": overall_progress,
            "current_step": get_current_step(
                profile_completion, document_completion, verification_status
            ),
        }

    def get_dashboard_context(self):
        user = self.request.user
        state = self.get_onboarding_state()
        profile = state["profile"]

        return {
            "page_title": self.page_title,
            "active_nav": self.active_nav,
            "employee_name": _value(user, "full_name", user.get_username()),
            "employee_id": _value(user, "employee_id", "Not assigned"),
            "department": _value(profile, "department", "Not assigned"),
            "joining_date": _value(profile, "joining_date", user.date_joined),
            "profile_completion": state["profile_completion"],
            "document_completion": state["document_completion"],
            "verification_status": state["verification_status"],
            "overall_status": user.get_display_status(),
            "notification_count": 0,
            "current_step": state["current_step"],
            "overall_progress": state["overall_progress"],
        }


class DashboardView(LoginRequiredMixin, DashboardContextMixin, TemplateView):
    template_name = "dashboard/dashboard.html"
    login_url = "login"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_dashboard_context())
        state = self.get_onboarding_state()
        context["timeline_steps"] = build_timeline(
            state["profile_completion"],
            state["document_completion"],
            state["verification_status"],
        )
        return context


class ProfileView(LoginRequiredMixin, DashboardContextMixin, TemplateView):
    template_name = "dashboard/profile.html"
    login_url = "login"
    page_title = "Profile"
    active_nav = "profile"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_dashboard_context())
        profile = get_employee_profile(self.request.user)

        context.update(
            {
                "personal_details": [
                    ("Full name", context["employee_name"]),
                    ("Employee ID", context["employee_id"]),
                    ("Department", context["department"]),
                    ("Designation", _value(profile, "designation", "Not provided")),
                    ("Status", context["overall_status"]),
                ],
                "contact_details": [
                    ("Personal email", self.request.user.personal_email),
                    (
                        "Company email",
                        _value(self.request.user, "company_email", "Not assigned"),
                    ),
                    ("Phone", _value(profile, "phone_number", "Not provided")),
                    ("Address", _value(profile, "address", "Not provided")),
                    (
                        "Emergency contact",
                        _value(profile, "emergency_contact", "Not provided"),
                    ),
                ],
                "education_details": [
                    (
                        "Date of birth",
                        profile.date_of_birth.strftime("%d %b %Y")
                        if profile and profile.date_of_birth
                        else "Not provided",
                    ),
                    (
                        "Joining date",
                        profile.joining_date.strftime("%d %b %Y")
                        if profile and profile.joining_date
                        else context["joining_date"].strftime("%d %b %Y")
                        if hasattr(context["joining_date"], "strftime")
                        else context["joining_date"],
                    ),
                ],
            }
        )
        return context


class DocumentsView(LoginRequiredMixin, DashboardContextMixin, TemplateView):
    template_name = "dashboard/documents.html"
    login_url = "login"
    page_title = "Documents"
    active_nav = "documents"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_dashboard_context())
        document = get_user_document(self.request.user)
        context["documents"] = build_document_rows(document)
        return context


class ApprovalStatusView(LoginRequiredMixin, DashboardContextMixin, TemplateView):
    template_name = "dashboard/approval_status.html"
    login_url = "login"
    page_title = "Approval Status"
    active_nav = "approval_status"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_dashboard_context())
        user = self.request.user
        profile = get_employee_profile(user)
        document = get_user_document(user)
        context["approval_timeline"] = build_approval_timeline(user, profile, document)
        return context


class NotificationsView(LoginRequiredMixin, DashboardContextMixin, TemplateView):
    template_name = "dashboard/notifications.html"
    login_url = "login"
    page_title = "Notifications"
    active_nav = "notifications"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_dashboard_context())
        state = self.get_onboarding_state()
        notifications = []

        if state["profile_completion"] < 100:
            notifications.append(
                {
                    "title": "Complete your employee profile",
                    "meta": "Required action",
                    "read": False,
                }
            )
        if state["document_completion"] < 100:
            notifications.append(
                {
                    "title": "Upload pending onboarding documents",
                    "meta": "Required action",
                    "read": False,
                }
            )
        if state["verification_status"] == "Pending":
            notifications.append(
                {
                    "title": "HR started document review",
                    "meta": "Approval update",
                    "read": False,
                }
            )
        notifications.append(
            {
                "title": f"Profile completion is {state['profile_completion']}%",
                "meta": "Progress update",
                "read": True,
            }
        )

        context["notifications"] = notifications
        context["unread_count"] = sum(1 for item in notifications if not item["read"])
        context["notification_count"] = context["unread_count"]
        return context


class RequiredActionsView(LoginRequiredMixin, DashboardContextMixin, TemplateView):
    template_name = "dashboard/required_actions.html"
    login_url = "login"
    page_title = "Required Actions"
    active_nav = "required_actions"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_dashboard_context())
        state = self.get_onboarding_state()
        context["actions"] = build_required_actions(
            state["profile_completion"],
            state["document_completion"],
        )
        return context


class SettingsView(LoginRequiredMixin, DashboardContextMixin, TemplateView):
    template_name = "dashboard/settings.html"
    login_url = "login"
    page_title = "Settings"
    active_nav = "settings"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_dashboard_context())
        context["settings"] = [
            {
                "label": "Email notifications",
                "description": "Receive onboarding updates by email",
                "enabled": True,
            },
            {
                "label": "Document reminders",
                "description": "Get reminders for pending uploads",
                "enabled": True,
            },
            {
                "label": "Weekly summary",
                "description": "Receive a weekly progress digest",
                "enabled": False,
            },
        ]
        return context
