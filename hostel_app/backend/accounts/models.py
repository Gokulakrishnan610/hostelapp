from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver
import os

class Student(models.Model):
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female')
    )
    PAYMENT_STATUS_CHOICES = (
        ('No Request', 'No Request'),
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Failed', 'Failed')
    )
    YEAR_CHOICES = [
        ('1', '1st Year'),
        ('2', '2nd Year'),
        ('3', '3rd Year'),
        ('4', '4th Year'),
        ('PG1', 'PG 1st Year'),
        ('PG2', 'PG 2nd Year'),
        ('MBA1', 'MBA 1st Year'),
        ('MBA2', 'MBA 2nd Year'),
        ('PhD', 'PhD'),
        ('Other', 'Other'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, default='')
    last_name = models.CharField(max_length=100, default='')
    name = models.CharField(max_length=255)
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES)
    email = models.EmailField(unique=True)
    department = models.CharField(max_length=100, default='')
    year = models.CharField(max_length=10, choices=YEAR_CHOICES, default='1')
    roll_number = models.CharField(max_length=50, default='')
    phone_number = models.CharField(max_length=15, default='')
    parent_phone_number = models.CharField(max_length=15, default='')
    room = models.ForeignKey('rooms.Room', on_delete=models.SET_NULL, null=True, blank=True)
    payment_status = models.CharField(
        max_length=15,
        choices=PAYMENT_STATUS_CHOICES,
        default='No Request'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Auto-generate full name if not explicitly set
        if not self.name:
            self.name = f"{self.first_name} {self.last_name}".strip()
        super().save(*args, **kwargs)

@receiver(pre_save, sender=Student)
def create_user_for_student(sender, instance, **kwargs):
    if not instance.pk and not hasattr(instance, 'user'):  # Only for new students
        user = User.objects.create_user(
            username=instance.email,
            email=instance.email,
            password='changeme@123',
            first_name=instance.name
        )
        instance.user = user

class OtpVerification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"OTP for {self.user.username}"

EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')