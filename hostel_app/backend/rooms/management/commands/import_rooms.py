from django.core.management.base import BaseCommand
from rooms.models import Room
from django.db import transaction
import decimal

class Command(BaseCommand):
    help = 'Import rooms data from initial SQL file'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        # Clear existing rooms if needed
        self.stdout.write('Clearing existing rooms...')
        Room.objects.all().delete()
        
        # Boys' Hostel data with prices
        boys_hostel_data = [
            {'category': '2 AC A', 'location': 'BH2', 'menu': 'Veg', 'rooms_count': 30, 'pax_per_room': 2, 'capacity': 60, 'available_seats': 60, 'price': decimal.Decimal('18000.00')},
            {'category': '3 Non AC C', 'location': 'Thandalam', 'menu': 'Non Veg', 'rooms_count': 2, 'pax_per_room': 3, 'capacity': 6, 'available_seats': 6, 'price': decimal.Decimal('15000.00')},
            {'category': '4 AC A', 'location': 'BH2', 'menu': 'Veg', 'rooms_count': 79, 'pax_per_room': 4, 'capacity': 316, 'available_seats': 316, 'price': decimal.Decimal('16000.00')},
            {'category': '4 Non AC A', 'location': 'Habitat', 'menu': 'Non Veg', 'rooms_count': 152, 'pax_per_room': 4, 'capacity': 608, 'available_seats': 608, 'price': decimal.Decimal('13000.00')},
            {'category': '5 Non AC C', 'location': 'Thandalam', 'menu': 'Non Veg', 'rooms_count': 27, 'pax_per_room': 5, 'capacity': 135, 'available_seats': 135, 'price': decimal.Decimal('12000.00')},
            {'category': '6 Non AC C', 'location': 'Habitat', 'menu': 'Non Veg', 'rooms_count': 240, 'pax_per_room': 6, 'capacity': 1440, 'available_seats': 1440, 'price': decimal.Decimal('10000.00')},
        ]
        
        # Girls' Hostel data with prices
        girls_hostel_data = [
            {'category': '2 AC A', 'location': 'GH1 (BH3)', 'menu': 'Veg', 'rooms_count': 6, 'pax_per_room': 2, 'capacity': 12, 'available_seats': 12, 'price': decimal.Decimal('18000.00')},
            {'category': '2 AC A', 'location': 'GH2', 'menu': 'Veg', 'rooms_count': 27, 'pax_per_room': 2, 'capacity': 54, 'available_seats': 54, 'price': decimal.Decimal('18000.00')},
            {'category': '2 AC A', 'location': 'GH3 (BH1)', 'menu': 'Veg', 'rooms_count': 6, 'pax_per_room': 2, 'capacity': 12, 'available_seats': 12, 'price': decimal.Decimal('18000.00')},
            {'category': '2 Non AC C', 'location': 'GH1 (BH3)', 'menu': 'Veg', 'rooms_count': 118, 'pax_per_room': 2, 'capacity': 236, 'available_seats': 236, 'price': decimal.Decimal('15000.00')},
            {'category': '2 Non AC C', 'location': 'GH3 (BH1)', 'menu': 'Veg', 'rooms_count': 43, 'pax_per_room': 2, 'capacity': 86, 'available_seats': 86, 'price': decimal.Decimal('15000.00')},
            {'category': '3 AC A', 'location': 'GH3 (BH1)', 'menu': 'Veg', 'rooms_count': 18, 'pax_per_room': 3, 'capacity': 36, 'available_seats': 36, 'price': decimal.Decimal('17000.00')},
            {'category': '3 Non AC C', 'location': 'GH3 (BH1)', 'menu': 'Veg', 'rooms_count': 80, 'pax_per_room': 3, 'capacity': 240, 'available_seats': 240, 'price': decimal.Decimal('14000.00')},
            {'category': '4 Non AC C', 'location': 'GH3 (BH1)', 'menu': 'Veg', 'rooms_count': 76, 'pax_per_room': 4, 'capacity': 304, 'available_seats': 304, 'price': decimal.Decimal('13000.00')},
            {'category': '4 Non AC C', 'location': 'GH2', 'menu': 'Veg', 'rooms_count': 178, 'pax_per_room': 4, 'capacity': 712, 'available_seats': 712, 'price': decimal.Decimal('13000.00')},
            {'category': '6 Non AC C', 'location': 'GH1 (BH3)', 'menu': 'Veg', 'rooms_count': 13, 'pax_per_room': 6, 'capacity': 78, 'available_seats': 78, 'price': decimal.Decimal('10000.00')},
        ]
        
        # Import boys' hostel data
        self.stdout.write('Importing boys\' hostel data...')
        for room_data in boys_hostel_data:
            Room.objects.create(**room_data)
            
        # Import girls' hostel data
        self.stdout.write('Importing girls\' hostel data...')
        for room_data in girls_hostel_data:
            Room.objects.create(**room_data)
            
        self.stdout.write(self.style.SUCCESS(f'Successfully imported {Room.objects.count()} rooms'))
