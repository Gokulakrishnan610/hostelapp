from django.db import models
from django.conf import settings
from accounts.models import Student
from rooms.models import Room
from django.utils import timezone

class BookingRequest(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Cancelled', 'Cancelled')
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='booking_requests')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='booking_requests')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    
    # Additional fields
    payment = models.ForeignKey('payments.Payment', on_delete=models.SET_NULL, null=True, blank=True, related_name='booking_request')
    admin_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_bookings')
    processed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Booking for {self.student.name} - {self.room.category} - {self.status}"
    
    def save(self, *args, **kwargs):
        # If status changing to Approved/Rejected and processed_at not set, set it now
        if self.pk:
            old_obj = BookingRequest.objects.get(pk=self.pk)
            if old_obj.status == 'Pending' and self.status in ['Approved', 'Rejected']:
                if not self.processed_at:
                    self.processed_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Booking Request"
        verbose_name_plural = "Booking Requests"
