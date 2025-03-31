from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from .models import Payment
from .serializers import PaymentSerializer
from accounts.models import Student
from rooms.models import Room

# Create your views here.

class PaymentViewSet(viewsets.ModelViewSet):
    """API endpoint for payments that can be viewed and created by students"""
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Payment.objects.filter(student__user=self.request.user)
    
    def perform_create(self, serializer):
        student = Student.objects.get(user=self.request.user)
        serializer.save(student=student, status='Pending')
        
        # Set a timer to automatically cancel the booking if payment is not verified
        # This would typically be done with Celery or another task queue
        # For simplicity, we'll just set the timestamp here
        payment = serializer.instance
        payment.created_at = timezone.now()
        payment.save()

class AdminPaymentViewSet(viewsets.ModelViewSet):
    """API endpoint for admins to manage payments"""
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAdminUser]
    
    @action(detail=True, methods=['post'])
    def verify_payment(self, request, pk=None):
        payment = self.get_object()
        
        # If payment is more than 24 hours old and still pending, mark as failed
        time_limit = timezone.now() - timedelta(hours=24)
        if payment.created_at < time_limit and payment.status == 'Pending':
            payment.status = 'Failed'
            
            # If there's a student with a room assignment linked to this payment
            if payment.student.room:
                # Increment available seats for the room
                room = payment.student.room
                room.available_seats += 1
                room.save()
                
                # Remove room assignment from student
                payment.student.room = None
                payment.student.payment_status = 'Failed'
                payment.student.save()
            
            payment.save()
            return Response({'detail': 'Payment expired and marked as failed'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Process verification
        payment.verified = True
        payment.status = 'Confirmed'
        payment.verification_date = timezone.now()
        payment.save()
        
        # Update student's payment status
        student = payment.student
        student.payment_status = 'Confirmed'
        student.save()
        
        return Response({'detail': 'Payment verified successfully'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def reject_payment(self, request, pk=None):
        payment = self.get_object()
        payment.status = 'Failed'
        payment.save()
        
        # Update student's payment status and free up the room
        student = payment.student
        if student.room:
            room = student.room
            room.available_seats += 1
            room.save()
            
            student.room = None
        
        student.payment_status = 'Failed'
        student.save()
        
        return Response({'detail': 'Payment rejected'}, status=status.HTTP_200_OK)
