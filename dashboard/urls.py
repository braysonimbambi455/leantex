from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Dashboard Home
    path('', views.dashboard_home, name='home'),
    
    # Role-specific Dashboards
    path('customer/', views.customer_dashboard, name='customer'),
    path('technician/', views.technician_dashboard, name='technician'),
    path('admin/', views.admin_dashboard, name='admin'),
    
    # Admin Booking Management
    path('admin/bookings/', views.manage_bookings, name='manage_bookings'),
    path('admin/assign/<int:booking_id>/', views.admin_assign_technician, name='admin_assign_technician'),
    path('admin/bulk-assign/', views.admin_bulk_assign, name='admin_bulk_assign'),
    path('admin/auto-assign-all/', views.admin_auto_assign_all, name='admin_auto_assign_all'),
    
    # Technician Job Management (AJAX Endpoints)
    path('technician/start-job/<int:booking_id>/', views.technician_start_job, name='technician_start_job'),
    path('technician/complete-job/<int:booking_id>/', views.technician_complete_job, name='technician_complete_job'),
    
    # Technician Job Management (Legacy/Redirect Endpoints)
    path('technician/accept/<int:booking_id>/', views.technician_accept_booking, name='technician_accept'),
    path('start-job/<int:booking_id>/', views.start_job, name='start_job'),
    path('complete-job/<int:booking_id>/', views.complete_job, name='complete_job'),
    
    # Support
    path('support/', views.support_request, name='support'),
]