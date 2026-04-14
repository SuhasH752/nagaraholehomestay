from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import RoomType, Room, Guest, Booking
from .services.availability import get_available_rooms_with_prices
from .serializers import RoomTypeSerializer, AvailabilityCheckSerializer, BookingCreateSerializer, BookingSerializer

def home(request):
    return render(request, 'booking/home.html')

def rooms_page(request):
    room_types = RoomType.objects.all()
    return render(request, 'booking/rooms.html', {'room_types': room_types})

@api_view(['GET'])
def room_types(request):
    types = RoomType.objects.all()
    serializer = RoomTypeSerializer(types, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def check_availability(request):
    serializer = AvailabilityCheckSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)
    
    data = serializer.validated_data
    available = get_available_rooms_with_prices(
        check_in=data['check_in'],
        check_out=data['check_out'],
        adults=data['adults'],
        children=data.get('children', 0),
        room_type_id=data.get('room_type_id')
    )
    return Response(available)

@api_view(['POST'])
def create_booking(request):
    serializer = BookingCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)
    
    data = serializer.validated_data
    
    # Check if room is still available
    from .services.availability import get_available_rooms
    available_rooms = get_available_rooms(
        data['check_in'], data['check_out'], 
        room_type_id=None, 
        adults=data['adults'], 
        children=data['children']
    )
    room = Room.objects.get(id=data['room_id'])
    if room not in available_rooms:
        return Response({'error': 'Room no longer available for selected dates'}, status=400)
    
    # Create or get guest
    guest_data = data['guest']
    guest, _ = Guest.objects.get_or_create(
        email=guest_data['email'],
        defaults={
            'first_name': guest_data['first_name'],
            'last_name': guest_data['last_name'],
            'phone': guest_data['phone'],
            'address': guest_data.get('address', '')
        }
    )
    
    # Calculate price
    from .services.availability import calculate_price
    room_type = room.room_type
    total_price = calculate_price(room_type, data['check_in'], data['check_out'], data['adults'], data['children'])
    total_nights = (data['check_out'] - data['check_in']).days
    
    # Create booking
    booking = Booking.objects.create(
        guest=guest,
        room=room,
        check_in=data['check_in'],
        check_out=data['check_out'],
        adults=data['adults'],
        children=data.get('children', 0),
        total_nights=total_nights,
        subtotal=total_price,
        total_amount=total_price,  # Add tax later if needed
        special_requests=data.get('special_requests', ''),
        status='pending'
    )
    
    return Response({
        'booking_id': booking.booking_id,
        'status': booking.status,
        'total_amount': float(booking.total_amount),
        'check_in': booking.check_in,
        'check_out': booking.check_out,
        'guest_name': f"{guest.first_name} {guest.last_name}",
        'message': 'Booking created successfully. Please complete payment to confirm.'
    }, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def booking_status(request, booking_id):
    try:
        booking = Booking.objects.get(booking_id=booking_id)
        serializer = BookingSerializer(booking)
        return Response(serializer.data)
    except Booking.DoesNotExist:
        return Response({'error': 'Booking not found'}, status=404)
    
def booking_form(request):
    room_type_id = request.GET.get('room_type')
    return render(request, 'booking/booking_form.html', {'room_type_id': room_type_id})
