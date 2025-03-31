from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Student, OtpVerification
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'roll_number', 'year', 'department', 'email', 'phone_number', 'gender', 'room_info', 'payment_status_colored', 'created_at')
    list_filter = ('gender', 'year', 'department', 'payment_status')
    search_fields = ('name', 'email', 'roll_number', 'phone_number', 'parent_phone_number')
    readonly_fields = ('created_at', 'updated_at', 'user')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('user', 'first_name', 'last_name', 'name', 'gender', 'email', 'phone_number', 'parent_phone_number')
        }),
        ('Academic Information', {
            'fields': ('department', 'year', 'roll_number')
        }),
        ('Accommodation', {
            'fields': ('room', 'payment_status')
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['reset_password_to_default']
    
    def reset_password_to_default(self, request, queryset):
        for student in queryset:
            student.user.set_password('changeme@123')
            student.user.save()
        self.message_user(request, f"Successfully reset password for {queryset.count()} student(s)")
    reset_password_to_default.short_description = "Reset password to default"

    def save_model(self, request, obj, form, change):
        if not change:  # Only for new students
            # Create new user with student email
            user = User.objects.create_user(
                username=obj.email,
                email=obj.email,
                password='changeme@123',
                first_name=obj.name,
                is_staff=False,
                is_superuser=False
            )
            obj.user = user
        super().save_model(request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'name' in form.base_fields:
            form.base_fields['name'].required = False
        return form

    def room_info(self, obj):
        if obj.room:
            url = reverse('admin:rooms_room_change', args=[obj.room.id])
            return format_html('<a href="{}">{} - {}</a>', 
                             url, obj.room.category, obj.room.location)
        return '-'
    room_info.short_description = 'Room'

    def payment_status_colored(self, obj):
        colors = {
            'No Request': '#808080',  # Gray
            'Pending': '#FFA500',     # Orange
            'Confirmed': '#28a745',   # Green
            'Failed': '#dc3545'       # Red
        }
        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(obj.payment_status, 'black'),
            obj.payment_status
        )
    payment_status_colored.short_description = 'Payment Status'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('room', 'user')

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }