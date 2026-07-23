from django.urls import path

from .views import (
    ApprovalStatusView,
    DashboardView,
    DocumentsView,
    NotificationsView,
    ProfileView,
    RequiredActionsView,
    SettingsView,
)

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
    path("profile/", ProfileView.as_view(), name="dashboard_profile"),
    path("documents/", DocumentsView.as_view(), name="dashboard_documents"),
    path("approval-status/", ApprovalStatusView.as_view(), name="dashboard_approval_status"),
    path("notifications/", NotificationsView.as_view(), name="dashboard_notifications"),
    path("required-actions/", RequiredActionsView.as_view(), name="dashboard_required_actions"),
    path("settings/", SettingsView.as_view(), name="dashboard_settings"),
]