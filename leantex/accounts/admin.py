from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib import messages
from django.db import transaction
from .models import Profile

class CustomUserAdmin(UserAdmin):
    actions = ['safe_delete_users', 'deactivate_users']
    
    def safe_delete_users(self, request, queryset):
        """Custom action to safely delete users"""
        deleted_count = 0
        skipped_count = 0
        
        with transaction.atomic():
            for user in queryset:
                # Check if user has related records
                from bookings.models import Booking
                from payments.models import Payment
                
                bookings = Booking.objects.filter(customer=user).count()
                payments = Payment.objects.filter(customer=user).count() if Payment.objects.exists() else 0
                
                if bookings == 0 and payments == 0:
                    # Safe to delete
                    user.delete()
                    deleted_count += 1
                else:
                    skipped_count += 1
                    self.message_user(
                        request,
                        f"Skipped {user.username}: has {bookings} bookings and {payments} payments",
                        level='WARNING'
                    )
        
        self.message_user(
            request,
            f"Successfully deleted {deleted_count} users. Skipped {skipped_count} users with related records."
        )
    
    safe_delete_users.short_description = "Safe delete selected users"
    
    def deactivate_users(self, request, queryset):
        """Deactivate selected users instead of deleting"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} users have been deactivated.")
    
    deactivate_users.short_description = "Deactivate selected users"

# Unregister the default User admin and register custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)