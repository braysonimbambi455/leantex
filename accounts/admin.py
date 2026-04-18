from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib import messages
from django.db import transaction
from .models import Profile

# Define an inline admin descriptor for Profile model
class ProfileInline(admin.StackedInline):
    """Display Profile fields on the User admin page"""
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ('phone_number', 'role', 'address', 'city', 'email_notifications', 'sms_notifications')

class CustomUserAdmin(UserAdmin):
    # Add the Profile inline to the User admin page
    inlines = [ProfileInline]
    
    actions = ['safe_delete_users', 'deactivate_users']
    
    # Optional: Add role to the list display
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_role')
    
    def get_role(self, obj):
        """Display the user's role in the list view"""
        if hasattr(obj, 'profile'):
            return obj.profile.role
        return 'No profile'
    get_role.short_description = 'Role'
    
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