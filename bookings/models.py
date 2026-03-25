from django.db import models
from django.contrib.auth.models import User
from services.models import Service
from django.utils import timezone
import random

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    booking_number = models.CharField(max_length=20, unique=True, editable=False)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings', null=True, blank=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='bookings')
    technician = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_bookings')
    
    # Booking details
    date = models.DateField()
    time = models.TimeField()
    duration = models.IntegerField(help_text="Duration in minutes", default=60)
    
    # Customer information
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=15)
    customer_address = models.TextField(blank=True)
    
    # Additional notes
    notes = models.TextField(blank=True, help_text="Special instructions or notes")
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    
    # Assignment tracking
    assigned_at = models.DateTimeField(null=True, blank=True)
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_bookings_by')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Notification tracking
    email_sent = models.BooleanField(default=False)
    sms_sent = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-date', '-time']
        indexes = [
            models.Index(fields=['status', 'date']),
            models.Index(fields=['technician', 'status']),
        ]

    def __str__(self):
        return f"Booking {self.booking_number} - {self.customer_name}"

    def save(self, *args, **kwargs):
        if not self.booking_number:
            # Generate booking number: LEX-YYYYMMDD-XXXX
            from django.utils.crypto import get_random_string
            date_str = timezone.now().strftime('%Y%m%d')
            random_str = get_random_string(4, allowed_chars='0123456789')
            self.booking_number = f"LEX-{date_str}-{random_str}"
        
        # Auto-assign technician if booking is confirmed and no technician assigned
        if self.status == 'confirmed' and not self.technician:
            self.auto_assign_technician()
        
        super().save(*args, **kwargs)

    def auto_assign_technician(self):
        """Automatically assign a technician based on availability and workload"""
        from django.contrib.auth.models import User
        from django.db.models import Count, Q
        
        # Get all active technicians
        technicians = User.objects.filter(
            profile__role='technician',
            is_active=True
        ).annotate(
            assigned_count=Count(
                'assigned_bookings',
                filter=Q(assigned_bookings__status__in=['assigned', 'in_progress'])
            )
        ).order_by('assigned_count')  # Technicians with least work first
        
        if technicians.exists():
            # Assign to technician with least workload
            self.technician = technicians.first()
            self.assigned_at = timezone.now()
            self.status = 'assigned'
            return True
        return False

    def assign_technician(self, technician, assigned_by=None):
        """Manually assign a technician"""
        self.technician = technician
        self.assigned_at = timezone.now()
        self.assigned_by = assigned_by
        self.status = 'assigned'
        self.save()
        
        # Send notification to technician
        self.send_assignment_notification()
        
        return True

    def send_assignment_notification(self):
        """Send notification to technician about new assignment"""
        if self.technician and self.technician.email:
            subject = f'New Service Assignment - {self.booking_number}'
            message = f"""
            Hello {self.technician.get_full_name() or self.technician.username},
            
            You have been assigned a new service booking.
            
            Booking Details:
            - Booking Number: {self.booking_number}
            - Customer: {self.customer_name}
            - Service: {self.service.name}
            - Date: {self.date}
            - Time: {self.time}
            - Duration: {self.duration} minutes
            - Location: {self.customer_address}
            
            Customer Contact:
            - Phone: {self.customer_phone}
            - Email: {self.customer_email}
            
            Special Instructions:
            {self.notes if self.notes else 'None'}
            
            Please log in to your dashboard to view more details and update the job status.
            
            Thank you,
            Leantex Management
            """
            
            try:
                from django.core.mail import send_mail
                from django.conf import settings
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [self.technician.email],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Error sending assignment email: {e}")