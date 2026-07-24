import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.http import JsonResponse

from employees.forms import ProfileForm
from employees.services.dashboard_service import DashboardService


@login_required
def profile_view(request):
    """View and edit employee profile with all sections."""

    employee = DashboardService.get_employee_profile(request.user)
    
    if not employee:
        messages.error(request, "Employee profile not found. Please contact HR.")
        return redirect("dashboard")

    profile_completion = DashboardService.calculate_profile_completion(employee)
    document_completion = DashboardService.calculate_document_completion(employee)
    notification_count = DashboardService.get_unread_notification_count(employee)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            profile = form.save(commit=False)
            # Recalculate completion after save
            profile.profile_completion_percentage = DashboardService.calculate_profile_completion(profile)
            profile.profile_completed = profile.profile_completion_percentage >= 100
            profile.save()
            
            # Update onboarding steps
            DashboardService.update_onboarding_steps(profile)
            
            # Create notification
            if profile.profile_completed:
                DashboardService.create_notification(
                    profile,
                    "Profile completed successfully",
                    "Your profile is now 100% complete. All information has been saved.",
                    "PROFILE",
                )
            
            messages.success(request, "Profile updated successfully!")
            return redirect("dashboard_profile")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ProfileForm(instance=employee)

    # Build profile sections for template
    profile_data = {
        "personal_information": [
            {"label": "First Name", "value": request.user.full_name.split()[0] if request.user.full_name else "—", "field": "first_name"},
            {"label": "Last Name", "value": " ".join(request.user.full_name.split()[1:]) if len(request.user.full_name.split()) > 1 else "—", "field": "last_name"},
            {"label": "Employee ID", "value": employee.employee_id, "field": "employee_id"},
            {"label": "Date of Birth", "value": employee.date_of_birth.strftime("%d %b %Y") if employee.date_of_birth else "Not provided", "field": "date_of_birth"},
            {"label": "Gender", "value": employee.get_gender_display() if employee.gender else "Not provided", "field": "gender"},
            {"label": "Phone Number", "value": employee.phone_number or "Not provided", "field": "phone_number"},
            {"label": "Alternate Number", "value": employee.alternate_number or "Not provided", "field": "alternate_number"},
            {"label": "Personal Email", "value": request.user.personal_email, "field": "personal_email"},
        ],
        "company_information": [
            {"label": "Company Email", "value": request.user.company_email or "Not assigned", "field": "company_email"},
            {"label": "Department", "value": employee.department or "Not assigned", "field": "department"},
            {"label": "Designation", "value": employee.designation or "Not assigned", "field": "designation"},
            {"label": "Joining Date", "value": employee.joining_date.strftime("%d %b %Y") if employee.joining_date else "Not set", "field": "joining_date"},
            {"label": "Reporting Manager", "value": employee.reporting_manager or "Not assigned", "field": "reporting_manager"},
        ],
        "address_information": [
            {"label": "Current Address", "value": employee.current_address or "Not provided", "field": "current_address"},
            {"label": "Permanent Address", "value": employee.permanent_address or "Not provided", "field": "permanent_address"},
            {"label": "City", "value": employee.city or "Not provided", "field": "city"},
            {"label": "State", "value": employee.state or "Not provided", "field": "state"},
            {"label": "Country", "value": employee.country or "Not provided", "field": "country"},
            {"label": "Pincode", "value": employee.pincode or "Not provided", "field": "pincode"},
        ],
        "emergency_contact": [
            {"label": "Contact Name", "value": employee.emergency_contact_name or "Not provided", "field": "emergency_contact_name"},
            {"label": "Relationship", "value": employee.emergency_contact_relationship or "Not provided", "field": "emergency_contact_relationship"},
            {"label": "Phone Number", "value": employee.emergency_contact_phone or "Not provided", "field": "emergency_contact_phone"},
        ],
    }

    context = {
        "form": form,
        "employee": employee,
        "profile_data": profile_data,
        "profile_data_json": json.dumps(profile_data),
        "employee_name": request.user.full_name,
        "employee_id": employee.employee_id,
        "department": employee.department or "Not assigned",
        "designation": employee.designation or "Not assigned",
        "joining_date": employee.joining_date if employee.joining_date else request.user.date_joined,
        "profile_completion": profile_completion,
        "document_completion": document_completion,
        "verification_status": DashboardService.get_verification_status(employee),
        "overall_progress": DashboardService.calculate_overall_progress(employee),
        "overall_status": request.user.get_display_status(),
        "notification_count": notification_count,
        "active_nav": "profile",
        "page_title": "Profile",
    }

    return render(request, "dashboard/profile.html", context)


@login_required
def update_profile_picture(request):
    """AJAX endpoint to upload/update profile picture."""
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Method not allowed"}, status=405)

    employee = DashboardService.get_employee_profile(request.user)
    if not employee:
        return JsonResponse({"success": False, "error": "Profile not found"}, status=404)

    if "profile_picture" not in request.FILES:
        return JsonResponse({"success": False, "error": "No image provided"}, status=400)

    image = request.FILES["profile_picture"]
    
    # Validate
    if not image.content_type.startswith("image/"):
        return JsonResponse({"success": False, "error": "File must be an image"}, status=400)
    
    if image.size > 5 * 1024 * 1024:  # 5MB
        return JsonResponse({"success": False, "error": "Image must be under 5MB"}, status=400)

    employee.profile_picture = image
    employee.save()

    return JsonResponse({
        "success": True,
        "image_url": employee.profile_picture.url,
    })

