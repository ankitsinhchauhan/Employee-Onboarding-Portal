from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from employees.forms import ProfileForm
from employees.services.dashboard_service import DashboardService


@login_required
def profile_view(request):
    """View and edit employee profile."""

    employee = DashboardService.get_employee_profile(request.user)
    profile_completion = DashboardService.calculate_profile_completion(employee)
    document_completion = 0
    notification_count = DashboardService.get_unread_notification_count(employee)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            profile = form.save(commit=False)
            # Recalculate completion after save
            profile.profile_completion_percentage = DashboardService.calculate_profile_completion(profile)
            profile.profile_completed = profile.profile_completion_percentage >= 100
            profile.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("dashboard_profile")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ProfileForm(instance=employee)

    context = {
        "form": form,
        "employee": employee,
        "employee_name": request.user.full_name,
        "employee_id": employee.employee_id if employee else "Not assigned",
        "department": employee.department if employee else "Not assigned",
        "designation": employee.designation if employee else "Not assigned",
        "joining_date": employee.joining_date if employee else request.user.date_joined,
        "profile_completion": profile_completion,
        "document_completion": document_completion,
        "verification_status": DashboardService.get_verification_status(employee),
        "overall_status": request.user.get_display_status(),
        "notification_count": notification_count,
        "active_nav": "profile",
        "page_title": "Profile",
    }

    return render(request, "dashboard/profile.html", context)

