from django.urls import path

from employees.views.dashboard import dashboard
from employees.views.documents_view import documents_view
from employees.views.notifications_view import (
    mark_all_notifications_read,
    mark_notification_read,
    notifications_view,
)
from employees.views.profile_view import profile_view
from employees.views.required_actions_view import required_actions_view
from employees.views.settings_view import settings_view

urlpatterns = [
    path("dashboard/", dashboard, name="dashboard"),
    path("profile/", profile_view, name="dashboard_profile"),
    path("documents/", documents_view, name="dashboard_documents"),
    path("notifications/", notifications_view, name="dashboard_notifications"),
    path(
        "notifications/<int:notification_id>/read/",
        mark_notification_read,
        name="mark_notification_read",
    ),
    path(
        "notifications/mark-all-read/",
        mark_all_notifications_read,
        name="mark_all_notifications_read",
    ),
    path(
        "required-actions/",
        required_actions_view,
        name="dashboard_required_actions",
    ),
    path("settings/", settings_view, name="dashboard_settings"),
]
