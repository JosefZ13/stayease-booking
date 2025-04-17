from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('booking/', views.booking, name='booking'),
    path('book/<int:room_id>/', views.booking_form, name='booking_form'),
    path('submit_booking/', views.submit_booking, name='submit_booking'),
    path('confirmation/<int:booking_id>/', views.booking_confirmation, name='booking_confirmation'),
    path('gallery/', views.gallery, name='gallery'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('edit-booking/<int:booking_id>/', views.edit_booking, name='edit_booking'),
    path('delete-booking/<int:booking_id>/', views.delete_booking, name='delete_booking'),
    path('room-search/', views.room_search, name='room_search'),
]
