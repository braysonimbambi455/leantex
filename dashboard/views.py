from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from bookings.models import Booking
from services.models import Service, Testimonial
from accounts.models import User, Profile
from payments.models import Payment
from datetime import timedelta, datetime
import logging

logger = logging.getLogger(__name__)

# ==================== DASHBOARD HOME ====================

@login_required
def dashboard_home(request):
    """
    Main dashboard view - redirects users to their specific dashboard based on role
    """
    user = request.user
    
    # Check if user has profile
    if not hasattr(user, 'profile'):
        messages.warning(request, 'Please complete your profile setup.')
        return redirect('accounts:profile')
    
    # Redirect based on role
    if user.profile.role == 'admin':
        return redirect('dashboard:admin')
    elif user.profile.role == 'technician':
        return redirect('dashboard:technician')
    else:  # customer
        return redirect('dashboard:customer')
    
    # Fallback (should never reach here)
    return redirect('index')


# ==================== CUSTOMER DASHBOARD ====================

@login_required
def customer_dashboard(request):
    """
    Customer dashboard showing their bookings, statistics, and quick actions
    """
    user = request.user
    
    # Get current date
    today = timezone.now().date()
    
    # Get user's bookings
    upcoming_bookings = Booking.objects.filter(
        customer=user,
        date__gte=today,
        status__in=['pending', 'confirmed', 'assigned', 'in_progress']
    ).select_related('service', 'technician').order_by('date', 'time')[:5]
    
    past_bookings = Booking.objects.filter(
        customer=user,
        status='completed'
    ).select_related('service', 'technician').order_by('-date', '-time')[:5]
    
    # Statistics
    total_bookings = Booking.objects.filter(customer=user).count()
    completed_bookings = Booking.objects.filter(customer=user, status='completed').count()
    pending_payments = Booking.objects.filter(
        customer=user, 
        payment_status='pending'
    ).count()
    
    # Add feedback tracking
    for booking in past_bookings:
        booking.feedback_given = hasattr(booking, 'testimonials') and booking.testimonials.exists() if hasattr(booking, 'testimonials') else False
    
    context = {
        'upcoming_bookings': upcoming_bookings,
        'past_bookings': past_bookings,
        'total_bookings': total_bookings,
        'completed_bookings': completed_bookings,
        'pending_payments': pending_payments,
        'now': timezone.now(),
    }
    return render(request, 'dashboard/customer_dashboard.html', context)


# ==================== TECHNICIAN DASHBOARD ====================

@login_required
def technician_dashboard(request):
    """
    Technician dashboard showing assigned jobs, schedule, and performance stats
    """
    if request.user.profile.role != 'technician':
        messages.error(request, 'Access denied. This area is for technicians only.')
        return redirect('dashboard:home')
    
    today = timezone.now().date()
    
    # Get today's bookings
    today_bookings = Booking.objects.filter(
        technician=request.user,
        date=today
    ).select_related('service', 'customer').order_by('time')
    
    # Get upcoming bookings
    upcoming_bookings = Booking.objects.filter(
        technician=request.user,
        date__gt=today,
        status__in=['assigned', 'confirmed']
    ).select_related('service', 'customer').order_by('date', 'time')
    
    # Get completed bookings
    completed_bookings = Booking.objects.filter(
        technician=request.user,
        status='completed'
    ).select_related('service').order_by('-date')[:10]
    
    # Statistics
    completed_today = Booking.objects.filter(
        technician=request.user,
        date=today,
        status='completed'
    ).count()
    
    monthly_completed = Booking.objects.filter(
        technician=request.user,
        status='completed',
        date__month=today.month,
        date__year=today.year
    ).count()
    
    # Weekly stats
    week_start = today - timedelta(days=today.weekday())
    weekly_count = Booking.objects.filter(
        technician=request.user,
        status='completed',
        date__gte=week_start
    ).count()
    weekly_target = 10  # Example target
    
    context = {
        'today_bookings': today_bookings,
        'upcoming_bookings': upcoming_bookings,
        'completed_bookings': completed_bookings,
        'completed_today': completed_today,
        'monthly_completed': monthly_completed,
        'weekly_count': weekly_count,
        'weekly_target': weekly_target,
        'now': timezone.now(),
    }
    return render(request, 'dashboard/technician_dashboard.html', context)


# ==================== ADMIN DASHBOARD ====================

@login_required
@staff_member_required
def admin_dashboard(request):
    """
    Admin dashboard showing business analytics, statistics, and management tools
    """
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')
    
    today = timezone.now().date()
    
    # Basic statistics
    total_customers = User.objects.filter(profile__role='customer').count()
    total_technicians = User.objects.filter(profile__role='technician').count()
    total_bookings = Booking.objects.count()
    total_revenue = Payment.objects.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Monthly statistics
    monthly_bookings = Booking.objects.filter(
        date__month=today.month,
        date__year=today.year
    ).count()
    
    new_customers = User.objects.filter(
        date_joined__month=today.month,
        date_joined__year=today.year
    ).count()
    
    # Pending tasks
    pending_bookings = Booking.objects.filter(status='pending').count()
    unassigned_bookings = Booking.objects.filter(technician__isnull=True, status='confirmed').count()
    
    # Status counts for chart
    status_counts = Booking.objects.values('status').annotate(count=Count('status'))
    
    # Recent bookings
    recent_bookings = Booking.objects.select_related('service', 'technician', 'customer').order_by('-created_at')[:10]
    
    # Popular services
    popular_services = Service.objects.annotate(
        booking_count=Count('bookings')
    ).order_by('-booking_count')[:5]
    
    # Technician performance
    technicians = User.objects.filter(profile__role='technician').annotate(
        completed_jobs=Count('assigned_bookings', filter=Q(assigned_bookings__status='completed')),
        assigned_jobs=Count('assigned_bookings', filter=~Q(assigned_bookings__status='completed')),
        avg_rating=Avg('assigned_bookings__testimonials__rating')
    )
    
    for tech in technicians:
        # Calculate current load percentage
        total_capacity = 10  # Example: max jobs per technician
        tech.current_load = (tech.assigned_jobs or 0) * 100 // total_capacity if total_capacity > 0 else 0
        tech.on_time_rate = 98  # Example static value
        
    completed_today = Booking.objects.filter(
        status='completed',
        date=today
    ).count()
    
    # Revenue by month (last 6 months)
    six_months_ago = timezone.now() - timedelta(days=180)
    monthly_revenue = []
    for i in range(6):
        month = (timezone.now() - timedelta(days=30*i)).strftime('%b')
        monthly_revenue.append({
            'month': month,
            'total': 100000 + (i * 50000)  # Example data - replace with actual query
        })
    
    context = {
        'total_customers': total_customers,
        'total_technicians': total_technicians,
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'monthly_bookings': monthly_bookings,
        'new_customers': new_customers,
        'pending_bookings': pending_bookings,
        'unassigned_bookings': unassigned_bookings,
        'status_counts': status_counts,
        'recent_bookings': recent_bookings,
        'popular_services': popular_services,
        'technicians': technicians,
        'completed_today': completed_today,
        'today_date': today,
        'monthly_revenue': monthly_revenue,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


# ==================== BOOKING MANAGEMENT ====================

@login_required
@staff_member_required
def manage_bookings(request):
    """
    Admin view to manage all bookings
    """
    bookings = Booking.objects.all().select_related('service', 'customer', 'technician').order_by('-date', '-time')
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        bookings = bookings.filter(status=status)
    
    # Filter by date
    date_from = request.GET.get('date_from')
    if date_from:
        bookings = bookings.filter(date__gte=date_from)
    
    date_to = request.GET.get('date_to')
    if date_to:
        bookings = bookings.filter(date__lte=date_to)
    
    # Get technicians for bulk assignment
    technicians = User.objects.filter(
        profile__role='technician',
        is_active=True
    ).annotate(
        assigned_count=Count(
            'assigned_bookings',
            filter=Q(assigned_bookings__status__in=['assigned', 'in_progress'])
        )
    ).order_by('assigned_count')
    
    context = {
        'bookings': bookings,
        'technicians': technicians,
    }
    return render(request, 'dashboard/manage_bookings.html', context)


# ==================== TECHNICIAN ASSIGNMENT ====================

@login_required
@staff_member_required
def admin_assign_technician(request, booking_id):
    """
    Admin view to assign technician to a specific booking
    """
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Get all available technicians with their current workload
    technicians = User.objects.filter(
        profile__role='technician',
        is_active=True
    ).annotate(
        assigned_count=Count(
            'assigned_bookings',
            filter=Q(assigned_bookings__status__in=['assigned', 'in_progress'])
        ),
        completed_count=Count(
            'assigned_bookings',
            filter=Q(assigned_bookings__status='completed')
        ),
        avg_rating=Avg('assigned_bookings__testimonials__rating')
    ).order_by('assigned_count')
    
    if request.method == 'POST':
        technician_id = request.POST.get('technician')
        if technician_id:
            technician = get_object_or_404(User, id=technician_id)
            
            # Assign technician
            booking.assign_technician(technician, assigned_by=request.user)
            
            messages.success(
                request, 
                f'Technician {technician.get_full_name() or technician.username} assigned to booking {booking.booking_number}'
            )
            
            return redirect('dashboard:manage_bookings')
        else:
            messages.error(request, 'Please select a technician.')
    
    context = {
        'booking': booking,
        'technicians': technicians,
    }
    return render(request, 'dashboard/admin_assign_technician.html', context)


@login_required
@staff_member_required
def admin_bulk_assign(request):
    """
    Bulk assign technicians to multiple bookings
    """
    if request.method == 'POST':
        booking_ids = request.POST.getlist('bookings')
        technician_id = request.POST.get('technician')
        
        if not booking_ids:
            messages.error(request, 'Please select at least one booking.')
            return redirect('dashboard:manage_bookings')
        
        if not technician_id:
            messages.error(request, 'Please select a technician.')
            return redirect('dashboard:manage_bookings')
        
        technician = get_object_or_404(User, id=technician_id)
        bookings = Booking.objects.filter(id__in=booking_ids, status='confirmed')
        
        assigned_count = 0
        for booking in bookings:
            booking.assign_technician(technician, assigned_by=request.user)
            assigned_count += 1
        
        messages.success(
            request, 
            f'Successfully assigned {assigned_count} bookings to {technician.get_full_name() or technician.username}'
        )
        
        return redirect('dashboard:manage_bookings')
    
    return redirect('dashboard:manage_bookings')


@login_required
@staff_member_required
def admin_auto_assign_all(request):
    """
    Auto-assign technicians to all unassigned confirmed bookings
    """
    unassigned_bookings = Booking.objects.filter(
        status='confirmed',
        technician__isnull=True
    ).order_by('date', 'time')
    
    assigned_count = 0
    for booking in unassigned_bookings:
        if booking.auto_assign_technician():
            assigned_count += 1
    
    messages.success(
        request, 
        f'Auto-assignment complete: {assigned_count} bookings assigned to technicians.'
    )
    
    return redirect('dashboard:manage_bookings')


# ==================== TECHNICIAN JOB ACTIONS ====================

@login_required
def technician_accept_booking(request, booking_id):
    """
    Technician accepts an assigned booking
    """
    if not request.user.profile.role == 'technician':
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')
    
    booking = get_object_or_404(Booking, id=booking_id, technician=request.user)
    
    if booking.status == 'assigned':
        booking.status = 'in_progress'
        booking.save()
        messages.success(request, f'Booking {booking.booking_number} accepted and now in progress.')
        
        # Notify customer
        try:
            from django.core.mail import send_mail
            subject = f'Technician Started - Booking {booking.booking_number}'
            message = f"""
            Dear {booking.customer_name},
            
            Your technician {request.user.get_full_name() or request.user.username} has started working on your service.
            
            Booking Details:
            - Service: {booking.service.name}
            - Date: {booking.date}
            - Time: {booking.time}
            
            The technician is on the way. You can contact them at {request.user.profile.phone_number if hasattr(request.user, 'profile') else 'N/A'}.
            
            Thank you for choosing Leantex!
            """
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [booking.customer_email],
                fail_silently=True,
            )
        except Exception as e:
            logger.error(f"Error sending acceptance notification: {e}")
    
    return redirect('dashboard:technician')


@login_required
def start_job(request, booking_id):
    """
    Technician starts a job
    """
    if request.method == 'POST' and request.user.profile.role == 'technician':
        booking = get_object_or_404(Booking, id=booking_id, technician=request.user)
        booking.status = 'in_progress'
        booking.save()
        messages.success(request, 'Job started successfully.')
    return redirect('dashboard:technician')


@login_required
def complete_job(request, booking_id):
    """
    Technician completes a job
    """
    if request.method == 'POST' and request.user.profile.role == 'technician':
        booking = get_object_or_404(Booking, id=booking_id, technician=request.user)
        booking.status = 'completed'
        booking.save()
        messages.success(request, 'Job marked as completed.')
        
        # Notify customer
        try:
            from django.core.mail import send_mail
            subject = f'Job Completed - Booking {booking.booking_number}'
            message = f"""
            Dear {booking.customer_name},
            
            Your service has been completed by {request.user.get_full_name() or request.user.username}.
            
            Booking Details:
            - Service: {booking.service.name}
            - Date: {booking.date}
            
            Thank you for choosing Leantex! We would love to hear your feedback.
            Please log in to your account to leave a review.
            """
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [booking.customer_email],
                fail_silently=True,
            )
        except Exception as e:
            logger.error(f"Error sending completion notification: {e}")
    
    return redirect('dashboard:technician')


# ==================== SUPPORT REQUEST ====================

@login_required
def support_request(request):
    """
    Handle support requests from users
    """
    if request.method == 'POST':
        subject = request.POST.get('subject', 'No subject')
        message = request.POST.get('message', 'No message')
        
        # Get user info
        user = request.user
        user_info = f"""
User: {user.username}
Name: {user.get_full_name()}
Email: {user.email}
Phone: {user.profile.phone_number if hasattr(user, 'profile') else 'Not provided'}
Role: {user.profile.role if hasattr(user, 'profile') else 'Unknown'}
        """
        
        full_message = f"""
SUPPORT REQUEST FROM {user.username.upper()}

{user_info}

SUBJECT: {subject}

MESSAGE:
{message}

---
Sent from Leantex Support System
        """
        
        try:
            # Send email to support
            from django.core.mail import send_mail
            send_mail(
                subject=f'Support Request: {subject}',
                message=full_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['support@leantex.co.ke'],  # Change to your support email
                fail_silently=False,
            )
            
            # Send confirmation to user
            send_mail(
                subject='Support Request Received - Leantex',
                message=f"""
Dear {user.get_full_name() or user.username},

Thank you for contacting Leantex Support. We have received your request and will get back to you within 24 hours.

Your request details:
----------------------
Subject: {subject}
Message: {message}

Best regards,
Leantex Support Team
                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            
            messages.success(request, 'Your support request has been sent successfully. We will contact you soon.')
        except Exception as e:
            logger.error(f"Failed to send support email: {e}")
            messages.error(request, 'Failed to send support request. Please try again later or call us directly.')
        
        # Redirect based on user role
        if hasattr(user, 'profile'):
            if user.profile.role == 'admin':
                return redirect('dashboard:admin')
            elif user.profile.role == 'technician':
                return redirect('dashboard:technician')
        
        return redirect('dashboard:customer')
    
    # If not POST, redirect to appropriate dashboard
    return redirect('dashboard:home')