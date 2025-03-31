from rest_framework import serializers
from .models import Room, RoomPhoto

class RoomPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomPhoto
        fields = ['id', 'title', 'description', 'image', 'is_primary']

class RoomSerializer(serializers.ModelSerializer):
    gender = serializers.SerializerMethodField()
    photos = RoomPhotoSerializer(many=True, read_only=True)
    primary_photo = serializers.SerializerMethodField()
    
    class Meta:
        model = Room
        fields = [
            'id', 'category', 'location', 'menu', 'pax_per_room', 
            'available_seats', 'price', 'photos', 'primary_photo', 'gender',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at'] 

    def get_gender(self, obj):
        """Determine gender based on location"""
        if obj.location in ['GH1 (BH3)', 'GH2', 'GH3 (BH1)']:
            return 'Female'
        else:
            return 'Male'

    def get_primary_photo(self, obj):
        primary_photo = obj.photos.filter(is_primary=True).first()
        if not primary_photo:
            primary_photo = obj.photos.first()
        
        if primary_photo:
            return RoomPhotoSerializer(primary_photo).data
        return None 