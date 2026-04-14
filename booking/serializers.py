from rest_framework import serializers
from .models import RoomType, Booking, Guest, Room

class RoomTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomType
        fields = '__all__'

class GuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guest
        fields = ['id', 'first_name', 'last_name', 'email', 'phone', 'address']

class BookingSerializer(serializers.ModelSerializer):
    guest_details = GuestSerializer(source='guest', read_only=True)
    
    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ['booking_id', 'total_nights', 'subtotal', 'total_amount', 'created_at']

class AvailabilityCheckSerializer(serializers.Serializer):
    check_in = serializers.DateField()
    check_out = serializers.DateField()
    adults = serializers.IntegerField(min_value=1, default=2)
    children = serializers.IntegerField(min_value=0, default=0)
    room_type_id = serializers.IntegerField(required=False, allow_null=True)

class BookingCreateSerializer(serializers.Serializer):
    check_in = serializers.DateField()
    check_out = serializers.DateField()
    adults = serializers.IntegerField(min_value=1)
    children = serializers.IntegerField(min_value=0, default=0)
    special_requests = serializers.CharField(required=False, allow_blank=True)
    room_id = serializers.IntegerField()
    guest = GuestSerializer()