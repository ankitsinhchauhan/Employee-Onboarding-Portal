from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from employees.forms import DocumentUploadForm
from employees.models import EmployeeDocument
from employees.services.dashboard_service import DashboardService


@login_required
def documents_view(request):
    """View and manage employee documents."""

    employee = DashboardService.get_employee_profile(request.user)
    documents = EmployeeDocument.objects.filter(employee=employee).order_by(
        "-uploaded_at"
    )

    profile_completion = DashboardService.calculate_profile_completion(employee)
    document_completion = DashboardService.calculate_document_completion(employee)
    verification_status = DashboardService.get_verification_status(employee)
    notification_count = DashboardService.get_unread_notification_count(employee)

    if request.method == "POST":
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.employee = employee
            doc.save()
            messages.success(request, "Document uploaded successfully!")
            return redirect("dashboard_documents")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = DocumentUploadForm()

    # Build document rows for the template
    document_rows = []
    DOCUMENT_FIELD_MAP = {
        "RESUME": "Resume / CV",
        "AADHAAR": "Aadhaar Card",
        "PAN": "PAN Card",
        "DEGREE": "Degree Certificate",
        "PHOTO": "Profile Photo",
        "OFFER_LETTER": "Offer Letter",
        "OTHER": "Other",
    }

    for doc_type, doc_label in DOCUMENT_FIELD_MAP.items():
        existing = documents.filter(document_type=doc_type).first()
        if existing:
            document_rows.append(
                {
                    "name": doc_label,
                    "status": existing.get_verification_status_display(),
                    "uploaded": existing.uploaded_at.strftime("%d %b %Y"),
                    "id": existing.id,
                }
            )
        else:
            document_rows.append(
                {
                    "name": doc_label,
                    "status": "Not Uploaded",
                    "uploaded": "—",
                    "id": None,
                }
            )

    context = {
        "form": form,
        "documents": document_rows,
        "employee": employee,
        "employee_name": request.user.full_name,
        "employee_id": employee.employee_id if employee else "Not assigned",
        "department": employee.department if employee else "Not assigned",
        "joining_date": employee.joining_date if employee else request.user.date_joined,
        "profile_completion": profile_completion,
        "document_completion": document_completion,
        "verification_status": verification_status,
        "overall_status": request.user.get_display_status(),
        "notification_count": notification_count,
        "active_nav": "documents",
        "page_title": "Documents",
    }

    return render(request, "dashboard/documents.html", context)

