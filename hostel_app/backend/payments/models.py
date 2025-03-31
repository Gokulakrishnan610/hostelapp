from django.db import models
from accounts.models import Student
from rooms.models import Room

class Payment(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Failed', 'Failed')
    )

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payments')
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    verified = models.BooleanField(default=False)
    verification_date = models.DateTimeField(null=True, blank=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment of {self.amount} by {self.student.name} for {self.room.category}"

    class Meta:
        ordering = ['-payment_date']