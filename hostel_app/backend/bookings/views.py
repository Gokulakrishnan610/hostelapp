from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.contrib import messages
from .models import BookingRequest

# Create your views here.

@staff_member_required
def booking_dashboard(request):
    """Dashboard view for booking requests"""
    pending_count = BookingRequest.objects.filter(status='Pending').count()
    approved_count = BookingRequest.objects.filter(status='Approved').count()
    rejected_count = BookingRequest.objects.filter(status='Rejected').count()
    
    recent_bookings = BookingRequest.objects.all().order_by('-created_at')[:10]
    
    context = {
        'title': 'Booking Dashboard',
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'recent_bookings': recent_bookings,
    }
    
    return render(request, 'admin/booking_dashboard.html', context)
