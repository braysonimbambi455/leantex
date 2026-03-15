from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    # Booking creation - both authenticated and guest users
    path('create/', views.booking_create, name='create'),
    path('create/<int:service_id>/', views.booking_create, name='create_with_service'),
    
    # Booking management - authenticated users only
    path('list/', views.booking_list, name='list'),
    path('history/', views.booking_history, name='history'),
    path('<int:booking_id>/', views.booking_detail, name='detail'),
    path('<int:booking_id>/cancel/', views.booking_cancel, name='cancel'),
    path('<int:booking_id>/reschedule/', views.booking_reschedule, name='reschedule'),
    path('<int:booking_id>/invoice/', views.booking_invoice, name='invoice'),
]