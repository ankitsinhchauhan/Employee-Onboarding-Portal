from django.db import models
from accounts.models import User

# Create your models here.

class Document(models.Model):

    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    resume = models.FileField(
        upload_to='documents/resume/'
    )

    aadhaar_card = models.FileField(
        upload_to='documents/aadhaar/'
    )

    pan_card = models.FileField(
        upload_to='documents/pan/'
    )

    degree_certificate = models.FileField(
        upload_to='documents/degree/'
    )

    passport_photo = models.ImageField(
        upload_to='documents/photo/'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    remarks = models.TextField(
        blank=True,
        null=True
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.user.full_name