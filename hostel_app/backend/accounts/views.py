from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import Student, OtpVerification
from .serializers import StudentSerializer, UserSerializer, ChangePasswordSerializer
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
import random
import string
from django.core.mail import send_mail
from django.conf import settings
from rooms.models import Room
from payments.models import Payment
from bookings.models import BookingRequest

# Create your views here.

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Only allow students to see their own profiles"""
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return Student.objects.all()
        return Student.objects.filter(user=user)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get the current user's profile"""
        try:
            student = Student.objects.get(user=request.user)
            serializer = self.get_serializer(student)
            return Response(serializer.data)
        except Student.DoesNotExist:
            return Response(
                {'detail': 'Student profile not found for current user.'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['patch'])
    def update_profile(self, request):
        """Update the current user's profile"""
        try:
            student = Student.objects.get(user=request.user)
            
            # Only allow updating certain fields
            allowed_fields = ['first_name', 'last_name', 'phone_number', 'parent_phone_number']
            data_to_update = {}
            
            for field in allowed_fields:
                if field in request.data:
                    data_to_update[field] = request.data[field]
            
            # If both first name and last name are provided, update the full name
            if 'first_name' in data_to_update and 'last_name' in data_to_update:
                data_to_update['name'] = f"{data_to_update['first_name']} {data_to_update['last_name']}"
            
            # Update the student
            serializer = self.get_serializer(student, data=data_to_update, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            # Update the user model as well (first_name and last_name)
            user = student.user
            if 'first_name' in data_to_update:
                user.first_name = data_to_update['first_name']
            if 'last_name' in data_to_update:
                user.last_name = data_to_update['last_name']
            user.save()
            
            return Response(serializer.data)
        except Student.DoesNotExist:
            return Response(
                {'detail': 'Student profile not found for current user.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Change the current user's password"""
        user = request.user
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        
        if not current_password or not new_password:
            return Response(
                {'detail': 'Both current and new password are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Check if current password is correct
        if not user.check_password(current_password):
            return Response(
                {'detail': 'Current password is incorrect.'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Set new password
        user.set_password(new_password)
        user.save()
        
        return Response({'detail': 'Password changed successfully.'})
        
    def create(self, request, *args, **kwargs):
        """Override create to check permissions"""
        user = request.user
        if not user.is_staff and not user.is_superuser:
            return Response(
                {'detail': 'You do not have permission to create student profiles.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        """Override update to check permissions"""
        user = request.user
        instance = self.get_object()
        
        if not user.is_staff and not user.is_superuser and instance.user != user:
            return Response(
                {'detail': 'You do not have permission to update this student profile.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """Override destroy to check permissions"""
        user = request.user
        if not user.is_staff and not user.is_superuser:
            return Response(
                {'detail': 'You do not have permission to delete student profiles.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

class AdminStudentViewSet(viewsets.ModelViewSet):
    """API endpoint for admins to manage students"""
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAdminUser]
    
    @action(detail=True, methods=['post'])
    def reset_password(self, request, pk=None):
        student = self.get_object()
        user = student.user
        user.set_password('changeme@123')
        user.save()
        return Response({'detail': 'Password reset to default'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_student(request):
    try:
        # Check if the user is associated with a student account
        Student.objects.get(user=request.user)
        return Response({'status': 'verified'})
    except Student.DoesNotExist:
        return Response(
            {'detail': 'Access denied. This portal is for students only.'},
            status=status.HTTP_403_FORBIDDEN
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_otp(request):
    try:
        print("Processing OTP request")
        student = Student.objects.get(user=request.user)
        email = student.email
        print(f"Found student: {student.name}, email: {email}")
        
        # Generate 6-digit OTP
        otp = ''.join(random.choices(string.digits, k=6))
        print(f"Generated OTP: {otp}")
        
        # Save OTP to database
        print("Creating OTP verification record...")
        OtpVerification.objects.create(
            user=request.user,
            otp=otp
        )
        print("OTP record created successfully")
        
        # Send email with OTP
        print("Sending email...")
        subject = 'Student Portal - Room Booking Verification'
        message = f'''
        Hello {student.name},
        
        Your OTP for room booking verification is: {otp}
        
        This OTP is valid for 10 minutes.
        
        Regards,
        Student Hostel Management Team
        '''
        
        try:
            send_mail(
                subject,
                message, 
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            print("Email sent successfully")
        except Exception as e:
            print(f"Email error: {e}")
            print(f"OTP for testing: {otp}")  # Print OTP to console for testing
        
        return Response({'detail': 'OTP sent successfully'})
    
    except Student.DoesNotExist:
        print("Student not found")
        return Response(
            {'detail': 'Student not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        print(f"Error in request_otp: {e}")
        import traceback
        traceback.print_exc()
        return Response(
            {'detail': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_otp(request):
    otp = request.data.get('otp')
    
    if not otp:
        return Response(
            {'detail': 'OTP is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Get the latest OTP for this user that hasn't been used
        verification = OtpVerification.objects.filter(
            user=request.user,
            is_used=False
        ).order_by('-created_at').first()
        
        if not verification:
            return Response(
                {'detail': 'No active OTP found. Please request a new one.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if OTP is expired (10 minutes validity)
        if (timezone.now() - verification.created_at).total_seconds() > 600:
            return Response(
                {'detail': 'OTP has expired. Please request a new one.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify OTP
        if verification.otp != otp:
            return Response(
                {'detail': 'Invalid OTP'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Mark OTP as used
        verification.is_used = True
        verification.save()
        
        return Response({'detail': 'OTP verified successfully'})
    
    except Exception as e:
        print(f"Error in verify_otp: {e}")
        import traceback
        traceback.print_exc()
        return Response(
            {'detail': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def make_payment(request):
    room_id = request.data.get('room_id')
    transaction_id = request.data.get('transaction_id')
    
    if not all([room_id, transaction_id]):
        return Response(
            {'detail': 'Room ID and transaction ID are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        student = Student.objects.get(user=request.user)
        room = Room.objects.get(id=room_id)
        
        # Use the room's price as the payment amount
        amount = room.price
        
        # Check if room has available seats
        if room.available_seats <= 0:
            return Response(
                {'detail': 'This room has no available seats.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if student already has a room and payment is confirmed
        if student.room and student.payment_status == 'Confirmed':
            return Response(
                {'detail': 'You already have a confirmed room assignment.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # If student has a pending payment, cancel it first
        if student.payment_status == 'Pending':
            # Find and cancel any pending payments
            pending_payments = Payment.objects.filter(student=student, status='Pending')
            for payment in pending_payments:
                payment.status = 'Failed'
                payment.save()
                
                # If a room was reserved, release it
                if payment.room:
                    payment.room.available_seats += 1
                    payment.room.save()
            
            # Reset student's payment status
            student.payment_status = 'No Request'
            student.save()
        
        # Create new payment with room price
        payment = Payment.objects.create(
            student=student,
            room=room,
            amount=amount,  # Using the room's price
            transaction_id=transaction_id,
            status='Pending'
        )
        
        # Update room's available seats
        room.available_seats -= 1
        room.save()
        
        # Update student status
        student.payment_status = 'Pending'
        student.room = room  # Temporarily assign room
        student.save()
        
        # Create booking request
        BookingRequest.objects.create(
            student=student,
            room=room,
            amount=amount,
            transaction_id=transaction_id,
            payment=payment,
            status='Pending'
        )
        
        return Response({
            'detail': 'Payment submitted successfully. Your booking request is pending admin approval.',
            'payment_id': payment.id
        })
        
    except Student.DoesNotExist:
        return Response(
            {'detail': 'Student profile not found.'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Room.DoesNotExist:
        return Response(
            {'detail': 'Room not found.'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'detail': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def action_buttons(self, obj):
    # same code here
    return format_html(...)
