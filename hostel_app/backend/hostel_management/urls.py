"""
URL configuration for hostel_management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from accounts.views import StudentViewSet, AdminStudentViewSet, verify_student, request_otp, verify_otp, make_payment
from rooms.views import RoomViewSet, AdminRoomViewSet
from payments.views import PaymentViewSet, AdminPaymentViewSet
from .admin_views import (
    admin_dashboard,
    room_stats_view,
    payment_analytics_view,
    student_analytics_view,
    booking_requests as booking_request_view,
    approve_booking,
    reject_booking
)
from bookings.views import booking_dashboard
from django.conf import settings
from django.conf.urls.static import static

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'students', StudentViewSet, basename='student')
router.register(r'admin/students', AdminStudentViewSet, basename='admin-student')
router.register(r'rooms', RoomViewSet, basename='room')
router.register(r'admin/rooms', AdminRoomViewSet, basename='admin-room')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'admin/payments', AdminPaymentViewSet, basename='admin-payment')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin/dashboard/', admin_dashboard, name='admin-dashboard'),
    path('admin/room-stats/', room_stats_view, name='room-stats'),
    path('admin/payment-analytics/', payment_analytics_view, name='payment-analytics'),
    path('admin/student-analytics/', student_analytics_view, name='student-analytics'),
    path('api/', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api-auth/', include('rest_framework.urls')),
    path('api/student/change-password/', 
         StudentViewSet.as_view({'post': 'change_password'}), 
         name='student-change-password'),
    path('api/verify-student/', verify_student, name='verify-student'),
    path('api/student/request-otp/', request_otp, name='request-otp'),
    path('api/student/verify-otp/', verify_otp, name='verify-otp'),
    path('api/student/make-payment/', make_payment, name='make-payment'),
    path('admin/booking-requests/', booking_request_view, name='admin_booking_requests'),
    path('admin/booking-requests/approve/<int:payment_id>/', approve_booking, name='admin_approve_booking'),
    path('admin/booking-requests/reject/<int:payment_id>/', reject_booking, name='admin_reject_booking'),
    path('admin/booking-dashboard/', booking_dashboard, name='booking-dashboard'),
]

# Add this at the end of the file
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
