from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
import uuid

class RoomType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    base_price = models.DecimalField(max_digits=8, decimal_places=2, help_text="Price per night in INR")
    max_adults = models.PositiveIntegerField(default=2)
    max_children = models.PositiveIntegerField(default=1)
    amenities = models.TextField(blank=True, help_text="Comma separated list")
    main_image = models.ImageField(upload_to='rooms/', blank=True, null=True, help_text="Main display image")
    
    def __str__(self):
        return self.name
    
class RoomImage(models.Model):
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='rooms/')
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"Image for {self.room_type.name}"

class Room(models.Model):
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.CharField(max_length=10, unique=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.room_type.name} - {self.room_number}"

class RatePlan(models.Model):
    name = models.CharField(max_length=100)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name='rate_plans')
    price_per_night = models.DecimalField(max_digits=8, decimal_places=2)
    valid_from = models.DateField()
    valid_to = models.DateField()
    min_stay = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} - {self.room_type.name}"

class BlockedDate(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='blocked_dates')
    date = models.DateField()
    reason = models.CharField(max_length=200, blank=True)
    
    class Meta:
        unique_together = ('room', 'date')
    
    def __str__(self):
        return f"{self.room.room_number} blocked on {self.date}"

class Guest(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('checked_in', 'Checked In'),
        ('checked_out', 'Checked Out'),
    ]
    
    booking_id = models.CharField(max_length=20, unique=True, editable=False)
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE, related_name='bookings')
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    check_in = models.DateField()
    check_out = models.DateField()
    adults = models.PositiveIntegerField()
    children = models.PositiveIntegerField(default=0)
    total_nights = models.PositiveIntegerField(editable=False, default=0)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    special_requests = models.TextField(blank=True)
    
    def save(self, *args, **kwargs):
        if not self.booking_id:
            self.booking_id = f"NH{timezone.now().strftime('%y%m%d')}{uuid.uuid4().hex[:6].upper()}"
        self.total_nights = (self.check_out - self.check_in).days
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.booking_id} - {self.guest}"