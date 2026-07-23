from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from employees.services.dashboard_service import DashboardService


@login_required
def dashboard(request):

    context = DashboardService.get_dashboard_data(
        request.user
    )

    context["active_nav"] = "dashboard"

    return render(
        request,
        "dashboard/dashboard.html",
        context
    )