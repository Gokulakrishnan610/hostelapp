from rest_framework import serializers
from .models import Payment
from accounts.serializers import StudentSerializer

class PaymentSerializer(serializers.ModelSerializer):
    student_details = StudentSerializer(source='student', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'student', 'student_details', 'amount', 
            'status', 'admin_verified', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'student', 'status', 'admin_verified', 'created_at', 'updated_at'] 