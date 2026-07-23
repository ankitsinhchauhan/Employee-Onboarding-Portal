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

    employee_id = models.CharField(max_length=20, unique=True)

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


    def __str__(self):
        return self.user.full_name

class EmployeeDocument(models.Model):

    employee = models.ForeignKey(
        EmployeeProfile,
        on_delete=models.CASCADE
    )

    document_name = models.CharField(max_length=100)

    file = models.FileField(upload_to="documents/")

    uploaded_at = models.DateTimeField(auto_now_add=True)

    verified = models.BooleanField(default=False)


class Notification(models.Model):

    employee = models.ForeignKey(
        EmployeeProfile,
        on_delete=models.CASCADE
    )

    title = models.CharField(max_length=200)

    message = models.TextField()

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)




class RequiredAction(models.Model):

    employee = models.ForeignKey(
        EmployeeProfile,
        on_delete=models.CASCADE
    )

    title = models.CharField(max_length=150)

    description = models.TextField()

    completed = models.BooleanField(default=False)