from datetime import date, timedelta
from django.db.models import Q
from booking.models import Room, Booking, BlockedDate, RatePlan, RoomType

def get_available_rooms(check_in: date, check_out: date, room_type_id=None, adults=2, children=0):
    """
    Returns list of Room objects available for the entire stay period.
    """
    nights = (check_out - check_in).days
    if nights <= 0:
        return Room.objects.none()

    # Rooms that are booked (overlapping dates)
    booked_rooms = Booking.objects.filter(
        status__in=['pending', 'confirmed', 'checked_in'],
        check_in__lt=check_out,
        check_out__gt=check_in
    ).values_list('room_id', flat=True)

    # Rooms that are blocked on any of the stay dates
    blocked_rooms = BlockedDate.objects.filter(
        date__range=(check_in, check_out - timedelta(days=1))
    ).values_list('room_id', flat=True)

    unavailable = set(booked_rooms) | set(blocked_rooms)

    queryset = Room.objects.filter(is_active=True).exclude(id__in=unavailable)
    
    if room_type_id:
        queryset = queryset.filter(room_type_id=room_type_id)
    
    # Filter by capacity
    valid_rooms = []
    for room in queryset:
        if room.room_type.max_adults >= adults and room.room_type.max_children >= children:
            valid_rooms.append(room)
    
    return valid_rooms

def calculate_price(room_type: RoomType, check_in: date, check_out: date, adults: int, children: int):
    """
    Calculate total price based on best available rate plan.
    """
    total_nights = (check_out - check_in).days
    base_price = room_type.base_price

    # Find applicable rate plan
    rate_plan = RatePlan.objects.filter(
        room_type=room_type,
        valid_from__lte=check_in,
        valid_to__gte=check_out - timedelta(days=1),
        is_active=True
    ).first()

    nightly_price = rate_plan.price_per_night if rate_plan else base_price
    return nightly_price * total_nights

def get_available_rooms_with_prices(check_in, check_out, adults=2, children=0, room_type_id=None):
    """
    Returns list of available rooms with price calculation.
    """
    available_rooms = get_available_rooms(check_in, check_out, room_type_id, adults, children)
    result = []
    seen_types = set()
    
    for room in available_rooms:
        room_type = room.room_type
        if room_type.id in seen_types:
            continue
        seen_types.add(room_type.id)
        
        total_price = calculate_price(room_type, check_in, check_out, adults, children)
        nightly_price = total_price / (check_out - check_in).days
        
        result.append({
            'room_id': room.id,
            'room_type_id': room_type.id,
            'room_type_name': room_type.name,
            'description': room_type.description,
            'max_adults': room_type.max_adults,
            'max_children': room_type.max_children,
            'amenities': room_type.amenities.split(',') if room_type.amenities else [],
            'base_price_per_night': float(room_type.base_price),
            'applied_price_per_night': float(nightly_price),
            'total_nights': (check_out - check_in).days,
            'total_price': float(total_price),
            'available_rooms_count': Room.objects.filter(room_type=room_type, is_active=True).exclude(id__in=[r.id for r in available_rooms if r.room_type == room_type]).count() + 1
        })
    
    return result