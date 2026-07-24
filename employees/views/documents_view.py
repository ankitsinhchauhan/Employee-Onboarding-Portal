import mimetypes
import os

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from employees.forms import DocumentUploadForm
from employees.models import EmployeeDocument
from employees.services.dashboard_service import DashboardService


@login_required
def documents_view(request):
    """View and manage employee documents with modern UI."""

    employee = DashboardService.get_employee_profile(request.user)
    if not employee:
        messages.error(request, "Employee profile not found. Please contact HR.")
        return redirect("dashboard")

    documents = EmployeeDocument.objects.filter(employee=employee).order_by("-uploaded_at")

    profile_completion = DashboardService.calculate_profile_completion(employee)
    document_completion = DashboardService.calculate_document_completion(employee)
    verification_status = DashboardService.get_verification_status(employee)
    notification_count = DashboardService.get_unread_notification_count(employee)

    if request.method == "POST":
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.employee = employee
            # Calculate file size
            if doc.file:
                doc.file_size = doc.file.size
            doc.save()
            
            # Update onboarding steps
            DashboardService.update_onboarding_steps(employee)
            
            # Create notification
            DashboardService.create_notification(
                employee,
                f"Document uploaded: {doc.document_name}",
                f"Your {doc.get_document_type_display()} has been uploaded successfully. It is pending verification.",
                "DOCUMENT",
            )
            
            messages.success(request, f"{doc.get_document_type_display()} uploaded successfully!")
            return redirect("dashboard_documents")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = DocumentUploadForm()

    # Build document cards with status details
    DOCUMENT_TYPE_CONFIG = {
        "AADHAAR": {"icon": "bi-credit-card-2-front", "color": "#f59e0b", "required": True},
        "PAN": {"icon": "bi-credit-card", "color": "#ef4444", "required": True},
        "PHOTO": {"icon": "bi-camera", "color": "#8b5cf6", "required": True},
        "DEGREE": {"icon": "bi-mortarboard", "color": "#06b6d4", "required": True},
        "RESUME": {"icon": "bi-file-earmark-person", "color": "#2563eb", "required": False},
        "EXPERIENCE": {"icon": "bi-briefcase", "color": "#16a34a", "required": False},
        "OFFER_LETTER": {"icon": "bi-envelope-paper", "color": "#e11d48", "required": False},
        "OTHER": {"icon": "bi-file-earmark", "color": "#64748b", "required": False},
    }

    document_cards = []
    for doc_type, config in DOCUMENT_TYPE_CONFIG.items():
        existing = documents.filter(document_type=doc_type).first()
        if existing:
            document_cards.append({
                "id": existing.id,
                "type": doc_type,
                "type_label": existing.get_document_type_display(),
                "name": existing.document_name,
                "icon": config["icon"],
                "color": config["color"],
                "required": config["required"],
                "status": existing.verification_status,
                "status_label": existing.get_verification_status_display(),
                "uploaded_at": existing.uploaded_at,
                "uploaded_date": existing.uploaded_at.strftime("%d %b %Y, %I:%M %p"),
                "file_size": existing.file_size,
                "file_size_display": _format_file_size(existing.file_size),
                "file_url": existing.file.url,
                "is_image": existing.is_image(),
                "is_pdf": existing.is_pdf(),
                "extension": existing.get_file_extension(),
                "remarks": existing.remarks,
            })
        else:
            document_cards.append({
                "id": None,
                "type": doc_type,
                "type_label": dict(EmployeeDocument.DOCUMENT_TYPES).get(doc_type, doc_type),
                "name": None,
                "icon": config["icon"],
                "color": config["color"],
                "required": config["required"],
                "status": "NOT_UPLOADED",
                "status_label": "Not Uploaded",
                "uploaded_at": None,
                "uploaded_date": None,
                "file_size": 0,
                "file_size_display": "—",
                "file_url": None,
                "is_image": False,
                "is_pdf": False,
                "extension": None,
                "remarks": None,
            })

    # Calculate verification stats
    total_docs = len([c for c in document_cards if c["required"]])
    verified_docs = len([c for c in document_cards if c["status"] == "VERIFIED" and c["required"]])
    rejected_docs = len([c for c in document_cards if c["status"] == "REJECTED"])
    pending_docs = len([c for c in document_cards if c["status"] == "PENDING"])

    context = {
        "form": form,
        "document_cards": document_cards,
        "employee": employee,
        "document_stats": {
            "total": total_docs,
            "verified": verified_docs,
            "rejected": rejected_docs,
            "pending": pending_docs,
        },
        "employee_name": request.user.full_name,
        "employee_id": employee.employee_id,
        "department": employee.department or "Not assigned",
        "designation": employee.designation or "Not assigned",
        "joining_date": employee.joining_date if employee.joining_date else request.user.date_joined,
        "profile_completion": profile_completion,
        "document_completion": document_completion,
        "verification_status": verification_status,
        "overall_progress": DashboardService.calculate_overall_progress(employee),
        "overall_status": request.user.get_display_status(),
        "notification_count": notification_count,
        "active_nav": "documents",
        "page_title": "Documents",
    }

    return render(request, "dashboard/documents.html", context)


@login_required
@require_POST
def replace_document(request, document_id):
    """Replace an existing document's file."""
    employee = DashboardService.get_employee_profile(request.user)
    if not employee:
        return JsonResponse({"success": False, "error": "Profile not found"}, status=404)

    document = get_object_or_404(EmployeeDocument, id=document_id, employee=employee)

    if "file" not in request.FILES:
        return JsonResponse({"success": False, "error": "No file provided"}, status=400)

    new_file = request.FILES["file"]
    
    # Validate
    max_size = 10 * 1024 * 1024
    if new_file.size > max_size:
        return JsonResponse({"success": False, "error": "File size must be under 10MB"}, status=400)

    ext = new_file.name.split(".")[-1].lower()
    allowed = ["pdf", "jpg", "jpeg", "png", "doc", "docx"]
    if ext not in allowed:
        return JsonResponse({"success": False, "error": f"File type '.{ext}' not allowed"}, status=400)

    # Delete old file
    if document.file:
        if os.path.isfile(document.file.path):
            os.remove(document.file.path)

    document.file = new_file
    document.file_size = new_file.size
    document.verification_status = "PENDING"
    document.verified_by = None
    document.verified_at = None
    document.remarks = None
    document.save()

    # Create notification
    DashboardService.create_notification(
        employee,
        f"Document replaced: {document.document_name}",
        f"Your {document.get_document_type_display()} has been replaced. It is pending re-verification.",
        "DOCUMENT",
    )

    return JsonResponse({
        "success": True,
        "message": "Document replaced successfully",
        "file_url": document.file.url,
        "file_size_display": _format_file_size(document.file_size),
    })


@login_required
@require_POST
def delete_document(request, document_id):
    """Delete a document."""
    employee = DashboardService.get_employee_profile(request.user)
    if not employee:
        return JsonResponse({"success": False, "error": "Profile not found"}, status=404)

    document = get_object_or_404(EmployeeDocument, id=document_id, employee=employee)
    doc_name = document.document_name
    doc_type = document.get_document_type_display()

    # Delete file
    if document.file:
        if os.path.isfile(document.file.path):
            os.remove(document.file.path)

    document.delete()

    # Update onboarding steps
    DashboardService.update_onboarding_steps(employee)

    DashboardService.create_notification(
        employee,
        f"Document deleted: {doc_name}",
        f"Your {doc_type} has been deleted.",
        "DOCUMENT",
    )

    messages.success(request, f"{doc_type} deleted successfully.")
    return redirect("dashboard_documents")


@login_required
def preview_document(request, document_id):
    """Preview a document (inline view for PDF/images, download for other types)."""
    employee = DashboardService.get_employee_profile(request.user)
    if not employee:
        raise Http404("Profile not found")

    document = get_object_or_404(EmployeeDocument, id=document_id, employee=employee)

    if not document.file:
        raise Http404("File not found")

    file_path = document.file.path
    if not os.path.isfile(file_path):
        raise Http404("File not found on disk")

    content_type, _ = mimetypes.guess_type(file_path)
    if content_type is None:
        content_type = "application/octet-stream"

    response = FileResponse(open(file_path, "rb"), content_type=content_type)

    # Show inline for PDFs and images
    if document.is_pdf() or document.is_image():
        response["Content-Disposition"] = f'inline; filename="{document.document_name}{document.get_file_extension()}"'
    else:
        response["Content-Disposition"] = f'attachment; filename="{document.document_name}{document.get_file_extension()}"'

    return response


@login_required
def download_document(request, document_id):
    """Download a document."""
    employee = DashboardService.get_employee_profile(request.user)
    if not employee:
        raise Http404("Profile not found")

    document = get_object_or_404(EmployeeDocument, id=document_id, employee=employee)

    if not document.file:
        raise Http404("File not found")

    file_path = document.file.path
    if not os.path.isfile(file_path):
        raise Http404("File not found on disk")

    content_type, _ = mimetypes.guess_type(file_path)
    if content_type is None:
        content_type = "application/octet-stream"

    response = FileResponse(open(file_path, "rb"), content_type=content_type)
    response["Content-Disposition"] = f'attachment; filename="{document.document_name}{document.get_file_extension()}"'
    return response


def _format_file_size(size_bytes):
    """Format file size to human readable format."""
    if not size_bytes:
        return "—"
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"

