from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('customer/', views.customer_dashboard, name='customer'),
    path('technician/', views.technician_dashboard, name='technician'),
    path('admin/', views.admin_dashboard, name='admin'),
    path('admin/bookings/', views.manage_bookings, name='manage_bookings'),
    path('admin/assign/<int:booking_id>/', views.admin_assign_technician, name='admin_assign_technician'),
    path('admin/bulk-assign/', views.admin_bulk_assign, name='admin_bulk_assign'),
    path('admin/auto-assign-all/', views.admin_auto_assign_all, name='admin_auto_assign_all'),
    path('technician/accept/<int:booking_id>/', views.technician_accept_booking, name='technician_accept'),
    path('start-job/<int:booking_id>/', views.start_job, name='start_job'),
    path('complete-job/<int:booking_id>/', views.complete_job, name='complete_job'),
    path('support/', views.support_request, name='support'),
]