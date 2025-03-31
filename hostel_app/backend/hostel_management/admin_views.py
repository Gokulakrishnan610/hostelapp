from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Sum, F
from django.utils import timezone
from django.contrib import messages
from datetime import timedelta, date
from accounts.models import Student
from rooms.models import Room
from payments.models import Payment
from django.core.mail import send_mail
from django.conf import settings
from bookings.models import BookingRequest

@staff_member_required
def room_stats_view(request):
    context = {
        'title': 'Room Statistics',
        'room_stats': Room.objects.annotate(
            occupied=Count('student'),
            revenue=Sum('student__payment__amount', 
                       filter=models.Q(student__payment__status='Confirmed'))
        ).order_by('category'),
        'total_rooms': Room.objects.count(),
        'total_occupied': Room.objects.filter(available_seats__lt=F('capacity')).count(),
    }
    return render(request, 'admin/room_stats.html', context)

@staff_member_required
def payment_analytics_view(request):
    today = timezone.now().date()
    context = {
        'title': 'Payment Analytics',
        'total_revenue': Payment.objects.filter(status='Confirmed').aggregate(
            total=Sum('amount'))['total'] or 0,
        'today_payments': Payment.objects.filter(
            created_at__date=today).count(),
        'pending_payments': Payment.objects.filter(
            status='Pending').count(),
        'payment_stats': Payment.objects.values('status').annotate(
            count=Count('id'),
            total=Sum('amount')
        )
    }
    return render(request, 'admin/payment_analytics.html', context)

@staff_member_required
def student_analytics_view(request):
    context = {
        'title': 'Student Analytics',
        'total_students': Student.objects.count(),
        'gender_distribution': Student.objects.values('gender').annotate(
            count=Count('id')),
        'payment_status': Student.objects.values('payment_status').annotate(
            count=Count('id')),
        'recent_registrations': Student.objects.select_related(
            'room').order_by('-created_at')[:10]
    }
    return render(request, 'admin/student_analytics.html', context)

@staff_member_required
def admin_dashboard(request):
    today = timezone.now().date()
    
    # Calculate total rooms and occupancy
    total_rooms = Room.objects.count()
    occupied_rooms = Room.objects.filter(available_seats__lt=F('capacity')).count()
    occupancy_percentage = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0
    
    # Get recent activities
    recent_activities = []
    
    # Add recent students
    for student in Student.objects.select_related('room').order_by('-created_at')[:5]:
        recent_activities.append({
            'student_name': student.name,
            'action': 'Registration',
            'date': student.created_at,
            'status': student.payment_status
        })
    
    # Add recent payments
    for payment in Payment.objects.select_related('student').order_by('-created_at')[:5]:
        recent_activities.append({
            'student_name': payment.student.name,
            'action': 'Payment',
            'date': payment.created_at,
            'status': payment.status
        })
    
    # Sort combined activities by date
    recent_activities.sort(key=lambda x: x['date'], reverse=True)
    
    # Add pending bookings count
    pending_bookings_count = BookingRequest.objects.filter(status='Pending').count()
    recent_bookings = BookingRequest.objects.all()[:5]
    
    context = {
        'title': 'Dashboard',
        # Basic Stats
        'total_students': Student.objects.count(),
        'total_rooms': total_rooms,
        'occupied_rooms': occupied_rooms,
        'occupancy_percentage': round(occupancy_percentage, 1),
        'pending_payments': Payment.objects.filter(status='Pending').count(),
        
        # Recent Activities
        'recent_activities': recent_activities[:10],
        
        # Quick Stats
        'today_registrations': Student.objects.filter(created_at__date=today).count(),
        'total_revenue': Payment.objects.filter(status='Confirmed').aggregate(
            total=Sum('amount'))['total'] or 0,
        
        # Room Categories
        'room_categories': Room.objects.values('category').annotate(
            total=Count('id'),
            occupied=Count('student')
        ).order_by('category'),
        
        # Payment Stats
        'payment_stats': Payment.objects.values('status').annotate(
            count=Count('id'),
            total_amount=Sum('amount')
        ).order_by('status'),
        
        'pending_bookings_count': pending_bookings_count,
        'recent_bookings': recent_bookings,
    }
    return render(request, 'admin/dashboard.html', context)

def get_recent_activities():
    # Combine recent student registrations and payments
    activities = []
    
    for student in Student.objects.order_by('-created_at')[:5]:
        activities.append({
            'student_name': student.name,
            'action': 'Registration',
            'date': student.created_at
        })
    
    for payment in Payment.objects.order_by('-created_at')[:5]:
        activities.append({
            'student_name': payment.student.name,
            'action': f'Payment ({payment.status})',
            'date': payment.created_at
        })
    
    return sorted(activities, key=lambda x: x['date'], reverse=True)[:10]

@staff_member_required
def booking_requests(request):
    """View to show pending booking requests with approval/rejection options"""
    pending_payments = Payment.objects.filter(
        status='Pending', 
        verified=False
    ).select_related('student', 'room').order_by('-created_at')
    
    context = {
        'title': 'Booking Requests',
        'pending_payments': pending_payments,
    }
    
    return render(request, 'admin/booking_requests.html', context)

@staff_member_required
def approve_booking(request, payment_id):
    """Approve a booking request"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    if payment.status != 'Pending':
        messages.error(request, f"Cannot approve booking - status is {payment.status}")
        return redirect('admin:booking-requests')
        
    # Process approval
    payment.status = 'Confirmed'
    payment.verified = True
    payment.verification_date = timezone.now()
    payment.save()
    
    # Update student's payment status and room assignment
    student = payment.student
    student.payment_status = 'Confirmed'
    student.room = payment.room  # Ensure room is assigned
    student.save()
    
    # Send email notification
    subject = 'Room Booking Confirmed'
    message = f'''
    Hello {student.name},
    
    Congratulations! Your room booking has been confirmed.
    
    Room Details:
    - Category: {payment.room.category}
    - Location: {payment.room.location}
    - Menu: {payment.room.menu}
    
    Please contact the hostel administration if you have any questions.
    
    Regards,
    Student Hostel Management Team
    '''
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [student.email],
            fail_silently=True,
        )
    except Exception as e:
        print(f"Email error: {e}")
    
    return redirect('admin:booking-requests')

@staff_member_required
def reject_booking(request, payment_id):
    """Reject a booking request"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    if payment.status != 'Pending':
        messages.error(request, f"Cannot reject booking - status is {payment.status}")
        return redirect('admin:booking-requests')
    
    # Process rejection
    payment.status = 'Failed'
    payment.verified = True
    payment.verification_date = timezone.now()
    payment.save()
    
    # Update student's payment status
    student = payment.student
    student.payment_status = 'Failed'
    
    # If room was assigned, free it up
    if student.room and student.room.id == payment.room.id:
        # Increment available seats for the room
        room = student.room
        room.available_seats += 1
        room.save()
        
        # Remove room assignment
        student.room = None
    
    student.save()
    
    # Send email notification
    subject = 'Room Booking Request Declined'
    message = f'''
    Hello {student.name},
    
    We regret to inform you that your room booking request has been declined.
    
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
            [student.email],
            fail_silently=True,
        )
    except Exception as e:
        print(f"Email error: {e}")
    
    return redirect('admin:booking-requests')

# Add other helper functions for analytics... 