from django import forms
from .models import BookingRequest
from django.utils import timezone

class BookingRequestForm(forms.ModelForm):
    APPROVAL_CHOICES = (
        ('', '-- Select Action --'),
        ('approve', 'Approve Booking'),
        ('reject', 'Reject Booking'),
    )
    
    approval_action = forms.ChoiceField(choices=APPROVAL_CHOICES, required=False)
    admin_notes = forms.CharField(widget=forms.Textarea, required=False)
    
    class Meta:
        model = BookingRequest
        fields = ['admin_notes']
    
    def save(self, commit=True, user=None):
        booking = super().save(commit=False)
        
        action = self.cleaned_data.get('approval_action')
        
        if action == 'approve' and booking.status == 'Pending':
            booking.status = 'Approved'
            if user:
                booking.processed_by = user
                booking.processed_at = timezone.now()
            
            # Additional logic for approval
            if commit:
                booking.save()
                self._handle_approval(booking)
        
        elif action == 'reject' and booking.status == 'Pending':
            booking.status = 'Rejected'
            if user:
                booking.processed_by = user
                booking.processed_at = timezone.now()
            
            # Additional logic for rejection
            if commit:
                booking.save()
                self._handle_rejection(booking)
        
        elif commit:
            booking.save()
        
        return booking
    
    def _handle_approval(self, booking):
        # Update payment if exists
        if booking.payment:
            booking.payment.status = 'Confirmed'
            booking.payment.verified = True
            booking.payment.verification_date = timezone.now()
            booking.payment.save()
        
        # Update student's payment status and room assignment
        student = booking.student
        student.payment_status = 'Confirmed'
        student.room = booking.room
        student.save()
        
        # Send email notification
        self._send_approval_email(booking)
    
    def _handle_rejection(self, booking):
        # Update payment if exists
        if booking.payment:
            booking.payment.status = 'Failed'
            booking.payment.verified = True
            booking.payment.verification_date = timezone.now()
            booking.payment.save()
        
        # Update student's payment status
        student = booking.student
        student.payment_status = 'Failed'
        
        # If room was assigned, free it up
        if student.room and student.room.id == booking.room.id:
            # Increment available seats for the room
            room = student.room
            room.available_seats += 1
            room.save()
            
            # Remove room assignment
            student.room = None
        
        student.save()
        
        # Send email notification
        self._send_rejection_email(booking)
    
    def _send_approval_email(self, booking):
        # Email sending code (same as above)
        pass
    
    def _send_rejection_email(self, booking):
        # Email sending code (same as above)
        pass 