from django.contrib import admin
from django.urls import path
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.utils.html import format_html
from django.core.mail import send_mail
from django.conf import settings
from .models import BookingRequest
from .forms import BookingRequestForm

class HostelAdminSite(admin.AdminSite):
    site_header = 'Student Hostel Management System'
    site_title = 'Hostel Admin'
    index_title = 'Admin Dashboard'
    
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            # Add your custom admin URLs here
        ]
        return my_urls + urls

admin_site = HostelAdminSite(name='hostel_admin')

class BookingRequestAdmin(admin.ModelAdmin):
    list_display = ('student_info', 'room_info', 'amount', 'transaction_id', 'status_colored', 'created_at', 'actions')
    list_filter = ('status', 'created_at', 'room__category', 'room__location')
    search_fields = ('student__name', 'student__email', 'transaction_id', 'admin_notes')
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
    
    form = BookingRequestForm
    
    def student_info(self, obj):
        return format_html(
            '<strong>{}</strong><br>'
            '<small>{}</small><br>'
            '<small>Gender: {}</small>',
            obj.student.name,
            obj.student.email,
            obj.student.gender
        )
    student_info.short_description = 'Student'
    
    def room_info(self, obj):
        return format_html(
            '<strong>{} - {}</strong><br>'
            '<small>Menu: {}</small><br>'
            '<small>Capacity: {} persons</small>',
            obj.room.category,
            obj.room.location,
            obj.room.menu,
            obj.room.pax_per_room
        )
    room_info.short_description = 'Room'
    
    def status_colored(self, obj):
        colors = {
            'Pending': '#FFA500',    # Orange
            'Approved': '#28a745',   # Green
            'Rejected': '#dc3545',   # Red
            'Cancelled': '#6c757d',  # Gray
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.status, 'black'),
            obj.status
        )
    status_colored.short_description = 'Status'
    
    def actions(self, obj):
        if obj.status == 'Pending':
            return format_html(
                '<a class="button" style="background-color: #28a745; color: white;" '
                'href="{}">Approve</a> '
                '<a class="button" style="background-color: #dc3545; color: white;" '
                'href="{}">Reject</a>',
                f'/admin/hostel_management/bookingrequest/{obj.id}/approve/',
                f'/admin/hostel_management/bookingrequest/{obj.id}/reject/'
            )
        else:
            return format_html(
                '<span style="color: #6c757d;">Processed</span>'
            )
    actions.short_description = 'Actions'
    
    def approve_bookings(self, request, queryset):
        updated = 0
        for booking in queryset.filter(status='Pending'):
            self._process_approval(request, booking)
            updated += 1
        
        self.message_user(request, f"Successfully approved {updated} booking(s)")
    approve_bookings.short_description = "Approve selected bookings"
    
    def reject_bookings(self, request, queryset):
        updated = 0
        for booking in queryset.filter(status='Pending'):
            self._process_rejection(request, booking)
            updated += 1
        
        self.message_user(request, f"Successfully rejected {updated} booking(s)")
    reject_bookings.short_description = "Reject selected bookings"
    
    def _process_approval(self, request, booking):
        # Update booking status
        booking.status = 'Approved'
        booking.processed_by = request.user
        booking.processed_at = timezone.now()
        booking.save()
        
        # Update payment if exists
        if booking.payment:
            booking.payment.status = 'Confirmed'
            booking.payment.verified = True
            booking.payment.verification_date = timezone.now()
            booking.payment.save()
        
        # Update student's payment status and room assignment
        student = booking.student
        student.payment_status = 'Confirmed'
        student.room = booking.room  # Ensure room is assigned
        student.save()
        
        # Send email notification
        self._send_approval_email(booking)
    
    def _process_rejection(self, request, booking):
        # Update booking status
        booking.status = 'Rejected'
        booking.processed_by = request.user
        booking.processed_at = timezone.now()
        booking.save()
        
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
        subject = 'Room Booking Approved'
        message = f'''
        Hello {booking.student.name},
        
        Congratulations! Your room booking has been approved.
        
        Room Details:
        - Category: {booking.room.category}
        - Location: {booking.room.location}
        - Menu: {booking.room.menu}
        
        Amount Paid: ₹{booking.amount}
        Transaction ID: {booking.transaction_id}
        
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
        subject = 'Room Booking Request Rejected'
        message = f'''
        Hello {booking.student.name},
        
        We regret to inform you that your room booking request has been rejected.
        
        This may be due to verification issues with your payment information or room availability changes.
        
        Please contact the hostel administration for more information or to make a new booking.
        
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
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:booking_id>/approve/',
                self.admin_site.admin_view(self.approve_booking_view),
                name='hostel_management_bookingrequest_approve',
            ),
            path(
                '<int:booking_id>/reject/',
                self.admin_site.admin_view(self.reject_booking_view),
                name='hostel_management_bookingrequest_reject',
            ),
        ]
        return custom_urls + urls
    
    def approve_booking_view(self, request, booking_id):
        from django.shortcuts import get_object_or_404, redirect
        from django.contrib import messages
        
        booking = get_object_or_404(BookingRequest, id=booking_id)
        if booking.status == 'Pending':
            self._process_approval(request, booking)
            messages.success(request, f"Successfully approved booking for {booking.student.name}")
        else:
            messages.error(request, f"Cannot approve booking - status is {booking.status}")
        
        return redirect('admin:hostel_management_bookingrequest_changelist')
    
    def reject_booking_view(self, request, booking_id):
        from django.shortcuts import get_object_or_404, redirect
        from django.contrib import messages
        
        booking = get_object_or_404(BookingRequest, id=booking_id)
        if booking.status == 'Pending':
            self._process_rejection(request, booking)
            messages.success(request, f"Successfully rejected booking for {booking.student.name}")
        else:
            messages.error(request, f"Cannot reject booking - status is {booking.status}")
        
        return redirect('admin:hostel_management_bookingrequest_changelist')
    
    def save_model(self, request, obj, form, change):
        form.save(commit=True, user=request.user)

admin.site.register(BookingRequest, BookingRequestAdmin) 