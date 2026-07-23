from employees.models import (
    EmployeeProfile,
    EmployeeDocument,
    Notification,
    RequiredAction
)

class DashboardService:

    @staticmethod
    def get_dashboard_data(user):

        employee = EmployeeProfile.objects.get(user=user)

        total_docs = EmployeeDocument.objects.filter(
            employee=employee
        ).count()

        verified_docs = EmployeeDocument.objects.filter(
            employee=employee,
            verified=True
        ).count()

        notifications = Notification.objects.filter(
            employee=employee
        ).order_by("-created_at")[:5]

        actions = RequiredAction.objects.filter(
            employee=employee,
            completed=False
        )

        return {
            "employee": employee,
            "total_docs": total_docs,
            "verified_docs": verified_docs,
            "notifications": notifications,
            "actions": actions,
        }