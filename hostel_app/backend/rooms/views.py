from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Room
from .serializers import RoomSerializer

# Create your views here.

class RoomViewSet(viewsets.ModelViewSet):
    """API endpoint for rooms that can be viewed by students"""
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter rooms based on gender and availability"""
        queryset = Room.objects.filter(available_seats__gt=0)
        
        gender = self.request.query_params.get('gender')
        if gender:
            # Proper gender filtering based on location
            # Girls' hostels: GH1, GH2, GH3
            # Boys' hostels: BH1, BH2, Habitat, Thandalam
            if gender == 'Female':
                queryset = queryset.filter(
                    location__in=['GH1 (BH3)', 'GH2', 'GH3 (BH1)']
                )
            elif gender == 'Male':
                queryset = queryset.filter(
                    location__in=['BH1', 'BH2', 'Habitat', 'Thandalam']
                )
            
        menu = self.request.query_params.get('menu')
        if menu:
            queryset = queryset.filter(menu=menu)
            
        capacity = self.request.query_params.get('capacity')
        if capacity:
            queryset = queryset.filter(pax_per_room=capacity)
            
        return queryset

class AdminRoomViewSet(viewsets.ModelViewSet):
    """API endpoint for admins to manage rooms"""
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [permissions.IsAdminUser]
