from django.contrib import admin
from django.utils.html import format_html
from .models import RoomType, Room, RatePlan, BlockedDate, Guest, Booking, RoomImage

class RoomImageInline(admin.TabularInline):
    model = RoomImage
    extra = 1
    fields = ('image', 'caption', 'order')
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px;"/>', obj.image.url)
        return "-"
    image_preview.short_description = 'Preview'

@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'base_price', 'max_adults', 'max_children', 'display_main_image')
    search_fields = ('name',)
    list_filter = ('max_adults',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'base_price')
        }),
        ('Capacity', {
            'fields': ('max_adults', 'max_children')
        }),
        ('Amenities & Media', {
            'fields': ('amenities', 'main_image')
        }),
    )
    inlines = [RoomImageInline]
    
    def display_main_image(self, obj):
        if obj.main_image:
            return format_html('<img src="{}" style="max-height: 50px;"/>', obj.main_image.url)
        return "-"
    display_main_image.short_description = 'Main Image'

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_number', 'room_type', 'is_active')
    list_filter = ('room_type', 'is_active')
    search_fields = ('room_number',)

@admin.register(RatePlan)
class RatePlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'room_type', 'price_per_night', 'valid_from', 'valid_to', 'is_active')
    list_filter = ('room_type', 'is_active')
    search_fields = ('name',)

@admin.register(BlockedDate)
class BlockedDateAdmin(admin.ModelAdmin):
    list_display = ('room', 'date', 'reason')
    list_filter = ('room', 'date')

@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone')
    search_fields = ('email', 'phone')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'guest', 'room', 'check_in', 'check_out', 'status', 'total_amount')
    list_filter = ('status', 'check_in')
    search_fields = ('booking_id', 'guest__email')
    readonly_fields = ('booking_id', 'total_nights', 'subtotal', 'total_amount', 'created_at')
    fieldsets = (
        ('Booking Info', {
            'fields': ('booking_id', 'guest', 'room', 'check_in', 'check_out', 'adults', 'children')
        }),
        ('Pricing', {
            'fields': ('total_nights', 'subtotal', 'tax', 'total_amount')
        }),
        ('Status', {
            'fields': ('status', 'special_requests')
        }),
    )