from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect


def role_required(allowed_roles=None, login_url=None, raise_exception=False):
    """
    Decorator for views that checks whether the user has a specific role.
    Usage:
        @role_required(['ADMIN', 'HR'])
        def my_view(request):
            ...
    """
    if allowed_roles is None:
        allowed_roles = []

    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                if login_url:
                    return redirect(login_url)
                return redirect("login")

            if request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)

            if raise_exception:
                raise PermissionDenied("You do not have permission to access this page.")

            return redirect("dashboard")

        return _wrapped_view

    return decorator


def admin_required(function=None, login_url=None):
    """
    Decorator for views that checks whether the user is an admin.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.role == "ADMIN",
        login_url=login_url,
        redirect_field_name=REDIRECT_FIELD_NAME,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

