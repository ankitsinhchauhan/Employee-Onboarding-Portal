from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from employees.services.dashboard_service import DashboardService


@login_required
def dashboard(request):
    """Main dashboard view for authenticated employees with dynamic data."""

    context = DashboardService.get_dashboard_summary(request.user)

    if "error" in context:
        return render(request, "dashboard/dashboard.html", context)

    context["active_nav"] = "dashboard"
    context["page_title"] = "Dashboard"

    return render(request, "dashboard/dashboard.html", context)

