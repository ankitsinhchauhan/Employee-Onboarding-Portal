from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, personal_email, password=None, **extra_fields):
        if not personal_email:
            raise ValueError("Personal email is required")

        personal_email = self.normalize_email(personal_email)
        user = self.model(personal_email=personal_email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, personal_email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", User.Role.ADMIN)
        extra_fields.setdefault("status", User.Status.ACTIVE)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(personal_email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        UNASSIGNED = "UNASSIGNED", "Unassigned"
        EMPLOYEE = "EMPLOYEE", "Employee"
        HR = "HR", "HR"
        ADMIN = "ADMIN", "Admin"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        ACTIVE = "ACTIVE", "Active"
        SUSPENDED = "SUSPENDED", "Suspended"

    full_name = models.CharField(max_length=150)
    personal_email = models.EmailField(unique=True)
    company_email = models.EmailField(unique=True, null=True, blank=True)

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.UNASSIGNED)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    employee_id = models.CharField(max_length=50, blank=True, null=True)
    hr_id = models.CharField(max_length=50, blank=True, null=True)

    is_first_login = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "personal_email"
    REQUIRED_FIELDS = ["full_name"]

    def __str__(self):
        return self.company_email or self.personal_email

    def get_display_status(self):
        return self.get_status_display()


class AuditLog(models.Model):
    """Tracks administrative actions performed by users."""

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=50)
    details = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"

    def __str__(self):
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M')}] {self.action} by {self.user}"
