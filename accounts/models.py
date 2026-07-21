from django.db import models

# Create your models here.

class User(models.Model):

    ROLE_CHOICES = (
        ('Admin', 'Admin'),
        ('HR', 'HR'),
        ('Employee', 'Employee'),
    )

    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )

    full_name = models.CharField(max_length=100)

    personal_email = models.EmailField(
        unique=True
    )

    company_email = models.EmailField(
        unique=True,
        blank=True,
        null=True
    )

    password = models.CharField(
        max_length=255
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    user_id = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True
    )

    is_first_login = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.full_name

