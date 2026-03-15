from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.db.models import Q, Sum, Count
from .models import Booking
from .forms import BookingForm, GuestBookingForm
from services.models import Service
from payments.utils import create_payment_intent

def booking_create(request, service_id=None):
    """
    Create a new booking - accessible to both authenticated and guest users
    """
    service = None
    if service_id:
        service = get_object_or_404(Service, id=service_id, is_available=True)
    
    # Use different forms for authenticated vs guest users
    if request.user.is_authenticated:
        form_class = BookingForm
        initial_data = {'service': service} if service else {}
    else:
        form_class = GuestBookingForm
        initial_data = {'service': service} if service else {}
    
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            
            # Set customer info for authenticated users
            if request.user.is_authenticated:
                booking.customer = request.user
                booking.customer_name = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username
                booking.customer_email = request.user.email
                if hasattr(request.user, 'profile'):
                    booking.customer_phone = request.user.profile.phone_number
                    booking.customer_address = request.user.profile.address
            
            # Set duration from service
            if booking.service:
                booking.duration = booking.service.duration
            
            booking.save()
            messages.success(request, 'Booking created successfully! Please complete payment.')
            
            # Redirect to payment
            return redirect('payments:checkout', booking_id=booking.id)
        else:
            # Form is invalid, show errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = form_class(initial=initial_data)
    
    context = {
        'form': form,
        'service': service,
    }
    return render(request, 'booking_form.html', context)

@login_required
def booking_list(request):
    """
    List all bookings for the current user based on their role
    """
    user = request.user
    
    # Base queryset based on user role
    if hasattr(user, 'profile'):
        if user.profile.role == 'customer':
            bookings = Booking.objects.filter(customer=user).select_related('service', 'technician')
        elif user.profile.role == 'technician':
            bookings = Booking.objects.filter(technician=user).select_related('service', 'customer')
        else:  # admin
            bookings = Booking.objects.all().select_related('service', 'customer', 'technician')
    else:
        # Fallback for users without profile
        bookings = Booking.objects.filter(customer=user).select_related('service', 'technician')
    
    # Apply filters
    status = request.GET.get('status')
    if status:
        bookings = bookings.filter(status=status)
    
    date_from = request.GET.get('date_from')
    if date_from:
        bookings = bookings.filter(date__gte=date_from)
    
    date_to = request.GET.get('date_to')
    if date_to:
        bookings = bookings.filter(date__lte=date_to)
    
    # Order by most recent first
    bookings = bookings.order_by('-date', '-time')
    
    # Calculate statistics
    completed_count = bookings.filter(status='completed').count()
    pending_count = bookings.filter(status='pending').count()
    
    # Calculate total spent (only for paid bookings)
    total_spent = bookings.filter(
        payment_status='paid'
    ).aggregate(total=Sum('service__price'))['total'] or 0
    
    # Add feedback_given attribute to each booking
    for booking in bookings:
        booking.feedback_given = hasattr(booking, 'testimonials') and booking.testimonials.exists() if hasattr(booking, 'testimonials') else False
    
    context = {
        'bookings': bookings,
        'completed_count': completed_count,
        'pending_count': pending_count,
        'total_spent': total_spent,
    }
    return render(request, 'dashboard/bookings_list.html', context)

@login_required
def booking_detail(request, booking_id):
    """
    View details of a specific booking
    """
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Check permissions
    if hasattr(request.user, 'profile'):
        if request.user.profile.role == 'customer' and booking.customer != request.user:
            messages.error(request, 'You do not have permission to view this booking.')
            return redirect('bookings:list')
    elif booking.customer != request.user:
        messages.error(request, 'You do not have permission to view this booking.')
        return redirect('bookings:list')
    
    context = {
        'booking': booking,
    }
    return render(request, 'dashboard/booking_detail.html', context)

@login_required
def booking_cancel(request, booking_id):
    """
    Cancel a booking
    """
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Check permissions
    if hasattr(request.user, 'profile'):
        if request.user.profile.role == 'customer' and booking.customer != request.user:
            messages.error(request, 'You cannot cancel this booking.')
            return redirect('bookings:list')
    elif booking.customer != request.user:
        messages.error(request, 'You cannot cancel this booking.')
        return redirect('bookings:list')
    
    # Check if booking can be cancelled
    if booking.status in ['completed', 'cancelled']:
        messages.error(request, f'This booking cannot be cancelled as it is already {booking.status}.')
        return redirect('bookings:detail', booking_id=booking.id)
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        
        # Update booking status
        booking.status = 'cancelled'
        booking.save()
        
        # Send cancellation email if email exists
        if booking.customer_email:
            try:
                subject = f'Booking Cancelled - {booking.booking_number}'
                message = f"""
                Dear {booking.customer_name},
                
                Your booking has been cancelled successfully.
                
                Booking Details:
                - Booking Number: {booking.booking_number}
                - Service: {booking.service.name}
                - Date: {booking.date}
                - Time: {booking.time}
                
                Cancellation Reason: {reason if reason else 'Not specified'}
                
                If you have already made a payment, a refund will be processed within 5-7 business days.
                
                Thank you for choosing Leantex.
                """
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [booking.customer_email],
                    fail_silently=True,
                )
            except Exception as e:
                # Log error but don't stop the process
                print(f"Error sending cancellation email: {e}")
        
        messages.success(request, 'Booking cancelled successfully.')
        return redirect('bookings:detail', booking_id=booking.id)
    
    context = {
        'booking': booking,
    }
    return render(request, 'dashboard/booking_cancel.html', context)

@login_required
def booking_reschedule(request, booking_id):
    """
    Reschedule a booking (optional feature)
    """
    booking = get_object_or_404(Booking, id=booking_id, customer=request.user)
    
    if booking.status in ['completed', 'cancelled']:
        messages.error(request, 'Cannot reschedule a completed or cancelled booking.')
        return redirect('bookings:detail', booking_id=booking.id)
    
    if request.method == 'POST':
        new_date = request.POST.get('date')
        new_time = request.POST.get('time')
        
        if new_date and new_time:
            booking.date = new_date
            booking.time = new_time
            booking.status = 'pending'  # Reset status to pending for approval
            booking.save()
            
            messages.success(request, 'Booking rescheduled successfully. Please wait for confirmation.')
            return redirect('bookings:detail', booking_id=booking.id)
        else:
            messages.error(request, 'Please provide both date and time.')
    
    context = {
        'booking': booking,
    }
    return render(request, 'dashboard/booking_reschedule.html', context)

@login_required
def booking_history(request):
    """
    View booking history (alternative to booking_list)
    """
    user = request.user
    
    # Get all bookings for the user
    bookings = Booking.objects.filter(customer=user).select_related('service', 'technician')
    
    # Separate upcoming and past bookings
    today = timezone.now().date()
    upcoming_bookings = bookings.filter(date__gte=today).exclude(status='cancelled').order_by('date', 'time')
    past_bookings = bookings.filter(date__lt=today).order_by('-date', '-time')
    cancelled_bookings = bookings.filter(status='cancelled').order_by('-date', '-time')
    
    context = {
        'upcoming_bookings': upcoming_bookings,
        'past_bookings': past_bookings,
        'cancelled_bookings': cancelled_bookings,
    }
    return render(request, 'dashboard/booking_history.html', context)

@login_required
def booking_invoice(request, booking_id):
    """
    Generate invoice for a booking (optional feature)
    """
    booking = get_object_or_404(Booking, id=booking_id, customer=request.user)
    
    if booking.payment_status != 'paid':
        messages.error(request, 'Invoice is only available for paid bookings.')
        return redirect('bookings:detail', booking_id=booking.id)
    
    context = {
        'booking': booking,
        'company': {
            'name': 'Leantex Company Limited',
            'address': 'Nairobi, Kenya',
            'phone': '+254 700 000 000',
            'email': 'info@leantex.co.ke',
            'website': 'www.leantex.co.ke',
        }
    }
    return render(request, 'dashboard/booking_invoice.html', context)