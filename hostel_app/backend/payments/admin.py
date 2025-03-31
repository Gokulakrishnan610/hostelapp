from django.contrib import admin
from .models import Payment
from django.utils.html import format_html
from django.urls import reverse

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('student', 'room', 'amount', 'transaction_id', 'status', 'verified', 'created_at')
    list_filter = ('status', 'verified')
    search_fields = ('student__name', 'transaction_id')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Payment Details', {
            'fields': ('student', 'room', 'amount', 'transaction_id')
        }),
        ('Status', {
            'fields': ('status', 'verified', 'verification_date')
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_payments', 'reject_payments']
    
    def approve_payments(self, request, queryset):
        # Update both payment status and student payment status
        for payment in queryset:
            payment.status = 'Confirmed'
            payment.verified = True
            payment.save()
            
            # Update student payment status
            student = payment.student
            student.payment_status = 'Confirmed'
            student.save()
            
        self.message_user(request, f"Successfully approved {queryset.count()} payment(s)")
    approve_payments.short_description = "Approve selected payments"
    
    def reject_payments(self, request, queryset):
        # Update both payment status and student payment status
        for payment in queryset:
            payment.status = 'Failed'
            payment.verified = True
            payment.save()
            
            # Update student payment status
            student = payment.student
            student.payment_status = 'Failed'
            student.save()
            
            # Return the seat to the room's available seats
            room = payment.room
            if room:
                room.available_seats += 1
                room.save()
            
            # Remove room assignment from student
            student.room = None
            student.save()
            
        self.message_user(request, f"Successfully rejected {queryset.count()} payment(s)")
    reject_payments.short_description = "Reject selected payments"

    def student_name(self, obj):
        url = reverse('admin:accounts_student_change', args=[obj.student.id])
        return format_html('<a href="{}">{}</a>', url, obj.student.name)
    student_name.short_description = 'Student'

    def room_info(self, obj):
        url = reverse('admin:rooms_room_change', args=[obj.room.id])
        return format_html('<a href="{}">{} - {}</a>', 
                         url, obj.room.category, obj.room.location)
    room_info.short_description = 'Room'

    def verification_status(self, obj):
        if obj.verified:
            return format_html(
                '<span style="color: green;">✓ Verified</span>'
            )
        return format_html(
            '<span style="color: orange;">Pending</span>'
        )
    verification_status.short_description = 'Verification'

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }