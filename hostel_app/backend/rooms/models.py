from django.db import models
from django.utils import timezone
import os
from django.utils.text import slugify

class Room(models.Model):
    MENU_CHOICES = (
        ('Veg', 'Veg'),
        ('Non Veg', 'Non Veg')
    )

    category = models.CharField(max_length=50)
    location = models.CharField(max_length=50)
    menu = models.CharField(max_length=10, choices=MENU_CHOICES)
    rooms_count = models.IntegerField(default=0)
    pax_per_room = models.IntegerField(default=2)  # Default to 2 persons per room
    capacity = models.IntegerField()
    available_seats = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def save(self, *args, **kwargs):
        # Auto-calculate capacity if not set
        if not self.capacity:
            self.capacity = self.rooms_count * self.pax_per_room
        # Initialize available seats if not set
        if not self.available_seats:
            self.available_seats = self.capacity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.category} - {self.location}"

    class Meta:
        ordering = ['category', 'location']
        unique_together = ['category', 'location']  # Prevent duplicate room categories in same location

def room_photo_path(instance, filename):
    """Generate file path for room photos"""
    # Get filename extension
    ext = filename.split('.')[-1]
    # Create a slug from the room category and location
    slug = slugify(f"{instance.room.category}-{instance.room.location}")
    # Return the path with a unique filename
    return f'room_photos/{slug}/{instance.room.id}_{slugify(instance.title)}.{ext}'

class RoomPhoto(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='photos')
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to=room_photo_path)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.room.category}"
    
    class Meta:
        ordering = ['-is_primary', 'created_at']
        
    def save(self, *args, **kwargs):
        # If this photo is marked as primary, unmark other primary photos for this room
        if self.is_primary:
            RoomPhoto.objects.filter(room=self.room, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)