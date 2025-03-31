from django.contrib import admin
from django.db.models import Count, Sum, Q, F
from django.utils.html import format_html
from django.urls import path
from django.template.response import TemplateResponse
from .models import Room, RoomPhoto

# First define the RoomPhotoInline class before RoomAdmin
class RoomPhotoInline(admin.TabularInline):
    model = RoomPhoto
    extra = 1
    fields = ('title', 'image', 'is_primary', 'preview_image')
    readonly_fields = ('preview_image',)
    
    def preview_image(self, obj):
        if obj.image and obj.image.url:
            return format_html('<img src="{}" width="100" height="100" style="object-fit: cover;" />', obj.image.url)
        return "No Image"
    preview_image.short_description = "Preview"

# Then define the RoomAdmin with the inline
@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('category', 'location', 'rooms_count', 'pax_per_room', 
                   'capacity', 'available_seats', 'price', 'menu', 'occupancy_status', 'actions_column')
    list_filter = ('category', 'menu', 'location')
    search_fields = ('category', 'location')
    
    fieldsets = (
        ('Room Information', {
            'fields': ('category', 'location', 'menu')
        }),
        ('Capacity Details', {
            'fields': ('rooms_count', 'pax_per_room', 'capacity', 'available_seats')
        }),
        ('Pricing', {
            'fields': ('price',)
        }),
    )
    
    actions = ['mark_full', 'mark_available']
    inlines = [RoomPhotoInline]  # Now this works because RoomPhotoInline is defined above
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('room-stats/', self.admin_site.admin_view(self.room_stats_view),
                 name='room-stats'),
        ]
        return custom_urls + urls
    
    def room_stats_view(self, request):
        context = {
            'title': 'Room Statistics',
            'room_stats': Room.objects.annotate(
                occupied=Count('student'),
                revenue=Sum('student__payment__amount', 
                          filter=Q(student__payment__status='Confirmed'))
            ).order_by('category'),
            'total_rooms': Room.objects.count(),
            'total_occupied': Room.objects.filter(available_seats__lt=F('capacity')).count(),
            'opts': self.model._meta,
        }
        return TemplateResponse(request, 'admin/room_stats.html', context)
    
    def actions_column(self, obj):
        return format_html(
            '<a class="button" href="{}">View Details</a>&nbsp;'
            '<a class="button" href="{}">Manage Students</a>',
            f'/admin/rooms/room/{obj.id}/change/',
            f'/admin/accounts/student/?room__id__exact={obj.id}'
        )
    actions_column.short_description = 'Actions'
    
    def mark_full(self, request, queryset):
        for room in queryset:
            room.available_seats = 0
            room.save()
    mark_full.short_description = "Mark selected rooms as full"
    
    def mark_available(self, request, queryset):
        for room in queryset:
            room.available_seats = room.capacity
            room.save()
    mark_available.short_description = "Reset available seats to capacity"

    def occupancy_status(self, obj):
        if obj.available_seats == 0:
            return format_html('<span style="color: red;">Full</span>')
        elif obj.available_seats < obj.capacity * 0.2:
            return format_html('<span style="color: orange;">Almost Full</span>')
        return format_html('<span style="color: green;">Available</span>')
    occupancy_status.short_description = 'Status'

    def save_model(self, request, obj, form, change):
        if not obj.capacity:
            obj.capacity = obj.rooms_count * obj.pax_per_room
        if not obj.available_seats:
            obj.available_seats = obj.capacity
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            student_count=Count('student')
        )

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }

# Register the RoomPhoto model separately
@admin.register(RoomPhoto)
class RoomPhotoAdmin(admin.ModelAdmin):
    list_display = ('thumbnail', 'title', 'room_info', 'is_primary', 'created_at')
    list_filter = ('is_primary', 'room__category', 'room__location')
    search_fields = ('title', 'description', 'room__category')
    
    fieldsets = (
        ('Room Information', {
            'fields': ('room',)
        }),
        ('Photo Details', {
            'fields': ('title', 'description', 'image', 'is_primary')
        }),
        ('System Information', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at',)
    
    def thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return "No Image"
    thumbnail.short_description = "Thumbnail"
    
    def room_info(self, obj):
        return format_html(
            '{} - {}',
            obj.room.category,
            obj.room.location
        )
    room_info.short_description = 'Room'