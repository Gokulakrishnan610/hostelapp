from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from django.core.mail import send_mail
from django.conf import settings
from .models import BookingRequest
from django.urls import reverse
from django.db import transaction

class BookingRequestAdmin(admin.ModelAdmin):
    list_display = ('student_info', 'room_info', 'amount', 'transaction_id', 'status_colored', 'created_at', 'action_buttons')
    list_filter = ('status', 'created_at', 'room__category', 'room__location')
    search_fields = ('student__name', 'student__email', 'student__roll_number', 'transaction_id', 'admin_notes')
    readonly_fields = ('created_at', 'updated_at', 'processed_at', 'processed_by')
    
    fieldsets = (
        ('Student Information', {
            'fields': ('student',)
        }),
        ('Room Information', {
            'fields': ('room', 'amount')
        }),
        ('Payment Details', {
            'fields': ('transaction_id', 'payment')
        }),
        ('Status', {
            'fields': ('status', 'admin_notes')
        }),
        ('Processing Information', {
            'fields': ('processed_by', 'processed_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_bookings', 'reject_bookings']
    
    def student_info(self, obj):
        url = reverse('admin:accounts_student_change', args=[obj.student.id])
        return format_html(
            '<a href="{}">'
            '<strong>{}</strong><br>'
            '<small>{} - {}</small><br>'
            '<small>Phone: {}</small>'
            '</a>',
            url,
            obj.student.name,
            obj.student.department,
            obj.student.year,
            obj.student.phone_number
        )
    student_info.short_description = 'Student'
    
    def room_info(self, obj):
        url = reverse('admin:rooms_room_change', args=[obj.room.id])
        return format_html(
            '<a href="{}">'
            '<strong>{} - {}</strong><br>'
            '<small>Menu: {}</small><br>'
            '<small>Capacity: {} persons</small>'
            '</a>',
            url,
            obj.room.category,
            obj.room.location,
            obj.room.menu,
            obj.room.pax_per_room
        )
    room_info.short_description = 'Room'
    
    def status_colored(self, obj):
        colors = {
            'Pending': '#FFA500',     # Orange
            'Approved': '#28a745',    # Green
            'Rejected': '#dc3545',    # Red
            'Cancelled': '#808080'    # Gray
        }
        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(obj.status, 'black'),
            obj.status
        )
    status_colored.short_description = 'Status'
    
    def action_buttons(self, obj):
        if obj.status == 'Pending':
            approve_url = reverse('admin:bookings_bookingrequest_approve', args=[obj.id])
            reject_url = reverse('admin:bookings_bookingrequest_reject', args=[obj.id])
            return format_html(
                '<a class="button" href="{}">Approve</a> '
                '<a class="button" style="background: #dc3545;" href="{}">Reject</a>',
                approve_url,
                reject_url
            )
        return '-'
    action_buttons.short_description = 'Actions'
    
    def approve_bookings(self, request, queryset):
        count = 0
        for booking in queryset.filter(status='Pending'):
            self._process_approval(request, booking)
            count += 1
        self.message_user(request, f"Successfully approved {count} booking(s)")
    approve_bookings.short_description = "Approve selected bookings"
    
    def reject_bookings(self, request, queryset):
        count = 0
        for booking in queryset.filter(status='Pending'):
            self._process_rejection(request, booking)
            count += 1
        self.message_user(request, f"Successfully rejected {count} booking(s)")
    reject_bookings.short_description = "Reject selected bookings"
    
    def _process_approval(self, request, booking):
        """Process booking approval, update all related records"""
        with transaction.atomic():
            # Update booking request
            booking.status = 'Approved'
            booking.processed_by = request.user
            booking.processed_at = timezone.now()
            booking.save()
            
            # Update payment
            if booking.payment:
                payment = booking.payment
                payment.status = 'Confirmed'
                payment.verified = True
                payment.verification_date = timezone.now()
                payment.save()
            
            # Update student
            student = booking.student
            student.payment_status = 'Confirmed'
            student.room = booking.room  # Ensure room is assigned
            student.save()
            
            # Send confirmation email
            self._send_confirmation_email(booking)
    
    def _process_rejection(self, request, booking):
        """Process booking rejection, update all related records"""
        with transaction.atomic():
            # Update booking request
            booking.status = 'Rejected'
            booking.processed_by = request.user
            booking.processed_at = timezone.now()
            booking.save()
            
            # Update payment
            if booking.payment:
                payment = booking.payment
                payment.status = 'Failed'
                payment.verified = True
                payment.verification_date = timezone.now()
                payment.save()
            
            # Return room to available seats
            room = booking.room
            room.available_seats += 1
            room.save()
            
            # Update student
            student = booking.student
            student.payment_status = 'Failed'
            student.room = None  # Remove room assignment
            student.save()
            
            # Send rejection email
            self._send_rejection_email(booking)
    
    def _send_confirmation_email(self, booking):
        """Send booking confirmation email"""
        subject = 'Room Booking Confirmed'
        message = f'''
        Hello {booking.student.name},
        
        Congratulations! Your room booking has been confirmed.
        
        Room Details:
        - Category: {booking.room.category}
        - Location: {booking.room.location}
        - Menu: {booking.room.menu}
        
        Please contact the hostel administration if you have any questions.
        
        Regards,
        Student Hostel Management Team
        '''
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [booking.student.email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Email error: {e}")
    
    def _send_rejection_email(self, booking):
        """Send booking rejection email"""
        subject = 'Room Booking Request Rejected'
        message = f'''
        Hello {booking.student.name},
        
        We regret to inform you that your room booking request has been rejected.
        
        If you have any questions about this decision, please contact the hostel administration.
        
        You can submit a new booking request for a different room if available.
        
        Regards,
        Student Hostel Management Team
        '''
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [booking.student.email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Email error: {e}")

admin.site.register(BookingRequest, BookingRequestAdmin)
