from django.urls import path

from employees.views.approval_status_view import approval_status_view
from employees.views.dashboard import dashboard
from employees.views.documents_view import (
    delete_document,
    documents_view,
    download_document,
    preview_document,
    replace_document,
)
from employees.views.notifications_view import (
    mark_all_notifications_read,
    mark_notification_read,
    notifications_view,
)
from employees.views.profile_view import profile_view, update_profile_picture
from employees.views.required_actions_view import required_actions_view
from employees.views.settings_view import settings_view

urlpatterns = [
    # Dashboard
    path("dashboard/", dashboard, name="dashboard"),
    
    # Profile
    path("profile/", profile_view, name="dashboard_profile"),
    path("profile/update-picture/", update_profile_picture, name="update_profile_picture"),
    
    # Documents
    path("documents/", documents_view, name="dashboard_documents"),
    path("documents/<int:document_id>/replace/", replace_document, name="replace_document"),
    path("documents/<int:document_id>/delete/", delete_document, name="delete_document"),
    path("documents/<int:document_id>/preview/", preview_document, name="preview_document"),
    path("documents/<int:document_id>/download/", download_document, name="download_document"),
    
    # Notifications
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
    
    # Required Actions
    path(
        "required-actions/",
        required_actions_view,
        name="dashboard_required_actions",
    ),
    
    # Approval Status
    path(
        "approval-status/",
        approval_status_view,
        name="dashboard_approval_status",
    ),
    
    # Settings
    path("settings/", settings_view, name="dashboard_settings"),
]

