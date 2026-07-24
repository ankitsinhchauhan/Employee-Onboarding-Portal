from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.decorators import role_required
from accounts.models import AuditLog
from .models import Department
from .forms import DepartmentForm

@login_required
@role_required(['ADMIN'])
def department_list_view(request):
    departments = Department.objects.all()
    return render(request, 'departments/list.html', {'departments': departments})


@login_required
@role_required(['ADMIN'])
def department_create_view(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            department = form.save()
            
            # Log action
            AuditLog.objects.create(
                user=request.user,
                action="DEPARTMENT_CREATE",
                details=f"Created department: {department.name} ({department.code})"
            )
            
            messages.success(request, f"Department '{department.name}' created successfully!")
            return redirect('departments:list')
    else:
        form = DepartmentForm()
    return render(request, 'departments/form.html', {'form': form, 'title': 'Create Department'})


@login_required
@role_required(['ADMIN'])
def department_update_view(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            
            # Log action
            AuditLog.objects.create(
                user=request.user,
                action="DEPARTMENT_UPDATE",
                details=f"Updated department: {department.name} ({department.code})"
            )
            
            messages.success(request, f"Department '{department.name}' updated successfully!")
            return redirect('departments:list')
    else:
        form = DepartmentForm(instance=department)
    return render(request, 'departments/form.html', {'form': form, 'title': 'Edit Department'})


@login_required
@role_required(['ADMIN'])
def department_delete_view(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        name = department.name
        code = department.code
        department.delete()
        
        # Log action
        AuditLog.objects.create(
            user=request.user,
            action="DEPARTMENT_DELETE",
            details=f"Deleted department: {name} ({code})"
        )
        
        messages.success(request, f"Department '{name}' deleted successfully!")
        return redirect('departments:list')
    return render(request, 'departments/confirm_delete.html', {'department': department})
