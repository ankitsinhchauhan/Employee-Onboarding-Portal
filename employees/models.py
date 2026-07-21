from django.db import models
from accounts.models import User

# Create your models here.

class EmployeeProfile(models.Model):

    DEPARTMENT_CHOICES = (
        ('IT', 'IT'),
        ('HR', 'HR'),
        ('Finance', 'Finance'),
        ('Marketing', 'Marketing'),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    department = models.CharField(
        max_length=50,
        choices=DEPARTMENT_CHOICES
    )

    designation = models.CharField(
        max_length=100
    )

    phone_number = models.CharField(
        max_length=15
    )

    address = models.TextField()

    date_of_birth = models.DateField()

    joining_date = models.DateField()

    emergency_contact = models.CharField(
        max_length=15
    )

    def __str__(self):
        return self.user.full_name