from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.views.generic import TemplateView


def _value(user, attribute, fallback):
	value = getattr(user, attribute, None)
	if value in (None, ""):
		return fallback
	return value


class DashboardContextMixin:
	page_title = "Dashboard"
	active_nav = "dashboard"

	def get_dashboard_context(self):
		user = self.request.user
		return {
			"page_title": self.page_title,
			"active_nav": self.active_nav,
			"employee_name": _value(user, "full_name", user.get_username()),
			"employee_id": _value(user, "employee_id", "EMP-1001"),
			"department": _value(user, "department", "Operations"),
			"joining_date": _value(user, "date_joined", timezone.now()),
			"profile_completion": int(_value(user, "profile_completion_percentage", 84)),
			"document_completion": int(_value(user, "document_completion_percentage", 72)),
			"verification_status": _value(user, "verification_status", "In Review"),
			"overall_status": _value(user, "status", "Pending"),
			"notification_count": int(_value(user, "notification_count", 4)),
			"current_step": _value(user, "current_step", "Document Verification"),
		}


class DashboardView(LoginRequiredMixin, DashboardContextMixin, TemplateView):
	template_name = "dashboard/dashboard.html"
	login_url = "login"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context.update(self.get_dashboard_context())
		context.update(
			{
				"overall_progress": 78,
				"timeline_steps": [
					{"title": "Profile submitted", "status": "completed", "note": "Employee details received"},
					{"title": "Documents uploaded", "status": "completed", "note": "PAN, Aadhaar, and photo on file"},
					{"title": "Document verification", "status": "current", "note": "HR review in progress"},
					{"title": "Manager approval", "status": "pending", "note": "Waiting for department sign-off"},
					{"title": "Welcome kit release", "status": "pending", "note": "Assets and workspace allocation"},
				],
			}
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
		context.update(
			{
				"personal_details": [
					("Full name", context["employee_name"]),
					("Employee ID", context["employee_id"]),
					("Department", context["department"]),
					("Status", context["overall_status"]),
				],
				"contact_details": [
					("Personal email", self.request.user.personal_email),
					("Company email", _value(self.request.user, "company_email", "pending@onboardhub.local")),
					("Phone", _value(self.request.user, "mobile_number", "+1 555 0100")),
					("Location", _value(self.request.user, "location", "Remote / Hybrid")),
				],
				"education_details": [
					("Highest qualification", _value(self.request.user, "education_level", "Bachelor's Degree")),
					("Institution", _value(self.request.user, "institution_name", "Northbridge University")),
					("Year of graduation", _value(self.request.user, "graduation_year", "2024")),
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
		context["documents"] = [
			{"name": "PAN Card", "status": "Approved", "uploaded": "12 Jul 2026"},
			{"name": "Aadhaar Card", "status": "Pending", "uploaded": "13 Jul 2026"},
			{"name": "Profile Photo", "status": "Approved", "uploaded": "13 Jul 2026"},
			{"name": "Address Proof", "status": "Rejected", "uploaded": "14 Jul 2026"},
		]
		return context


class ApprovalStatusView(LoginRequiredMixin, DashboardContextMixin, TemplateView):
	template_name = "dashboard/approval_status.html"
	login_url = "login"
	page_title = "Approval Status"
	active_nav = "approval_status"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context.update(self.get_dashboard_context())
		context["approval_timeline"] = [
			{"title": "Offer accepted", "status": "completed", "date": "10 Jul 2026"},
			{"title": "Profile validation", "status": "completed", "date": "12 Jul 2026"},
			{"title": "Document review", "status": "current", "date": "23 Jul 2026"},
			{"title": "HR approval", "status": "pending", "date": "Pending"},
			{"title": "Manager approval", "status": "pending", "date": "Pending"},
		]
		return context


class NotificationsView(LoginRequiredMixin, DashboardContextMixin, TemplateView):
	template_name = "dashboard/notifications.html"
	login_url = "login"
	page_title = "Notifications"
	active_nav = "notifications"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context.update(self.get_dashboard_context())
		context["unread_count"] = 3
		context["notifications"] = [
			{"title": "Upload your address proof", "meta": "Required action", "read": False},
			{"title": "HR started document review", "meta": "Approval update", "read": False},
			{"title": "Weekly onboarding summary available", "meta": "System notification", "read": True},
			{"title": "Profile completion increased to 84%", "meta": "Progress update", "read": True},
		]
		return context


class RequiredActionsView(LoginRequiredMixin, DashboardContextMixin, TemplateView):
	template_name = "dashboard/required_actions.html"
	login_url = "login"
	page_title = "Required Actions"
	active_nav = "required_actions"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context.update(self.get_dashboard_context())
		context["actions"] = [
			{"title": "Upload documents", "description": "Address proof and tax form pending", "icon": "cloud-upload", "button": "Upload Documents"},
			{"title": "Complete profile", "description": "Add emergency contact details", "icon": "person-check", "button": "Complete Profile"},
			{"title": "Download offer letter", "description": "Signed offer letter ready for download", "icon": "file-earmark-arrow-down", "button": "Download Offer Letter"},
			{"title": "View approval status", "description": "See the latest review progress", "icon": "clipboard-check", "button": "View Approval Status"},
		]
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
			{"label": "Email notifications", "description": "Receive onboarding updates by email", "enabled": True},
			{"label": "Document reminders", "description": "Get reminders for pending uploads", "enabled": True},
			{"label": "Weekly summary", "description": "Receive a weekly progress digest", "enabled": False},
		]
		return context
