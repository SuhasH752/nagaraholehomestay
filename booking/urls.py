from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('rooms/', views.rooms_page, name='rooms'),
    path('book/', views.booking_form, name='booking_form'),   # 👈 ADD THIS
    path('api/room-types/', views.room_types, name='room-types'),
    path('api/check-availability/', views.check_availability, name='check-availability'),
    path('api/create-booking/', views.create_booking, name='create-booking'),
    path('api/booking/<str:booking_id>/', views.booking_status, name='booking-status'),
]