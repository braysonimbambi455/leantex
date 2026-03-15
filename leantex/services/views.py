from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from bookings.models import Booking
from .models import Service, Category, Testimonial

def service_list(request):
    services = Service.objects.filter(is_available=True).select_related('category')
    categories = Category.objects.annotate(service_count=Count('services')).filter(service_count__gt=0)
    
    # Get selected category
    category_id = request.GET.get('category')
    selected_category = None
    if category_id and category_id.isdigit():
        selected_category = int(category_id)
        services = services.filter(category_id=selected_category)
    
    # Search functionality
    query = request.GET.get('q')
    if query:
        services = services.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(features__icontains=query)
        )
    
    # Sorting
    sort = request.GET.get('sort', 'name')
    if sort == 'price_low':
        services = services.order_by('price')
    elif sort == 'price_high':
        services = services.order_by('-price')
    elif sort == 'newest':
        services = services.order_by('-created_at')
    else:
        services = services.order_by('name')
    
    # Pagination
    paginator = Paginator(services, 12)  # Show 12 services per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get statistics
    total_services = services.count()
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': selected_category,
        'query': query,
        'sort': sort,
        'total_services': total_services,
    }
    return render(request, 'services.html', context)

def service_detail(request, pk):
    service = get_object_or_404(
        Service.objects.select_related('category').prefetch_related('testimonials'),
        pk=pk,
        is_available=True
    )
    
    # Get related services from same category
    related_services = Service.objects.filter(
        category=service.category,
        is_available=True
    ).exclude(pk=pk)[:4]
    
    # Get approved testimonials for this service
    testimonials = service.testimonials.filter(is_approved=True)[:5]
    
    context = {
        'service': service,
        'related_services': related_services,
        'testimonials': testimonials,
        'features': service.get_features_list(),
    }
    return render(request, 'service_detail.html', context)

def home_view(request):
    featured_services = Service.objects.filter(
        is_available=True
    ).select_related('category').order_by('-created_at')[:6]
    
    testimonials = Testimonial.objects.filter(
        is_approved=True
    ).select_related('service')[:5]
    
    categories = Category.objects.annotate(
        service_count=Count('services')
    ).filter(service_count__gt=0)[:6]
    
    context = {
        'featured_services': featured_services,
        'testimonials': testimonials,
        'categories': categories,
    }
    return render(request, 'index.html', context)


# --- New feedback submission view ---
@login_required
def submit_feedback(request, booking_id):
    if request.method == 'POST':
        booking = get_object_or_404(Booking, id=booking_id, customer=request.user)
        
        # Check if feedback already exists
        if Testimonial.objects.filter(service=booking.service, customer_name=request.user.get_full_name()).exists():
            messages.warning(request, 'You have already submitted feedback for this service.')
            return redirect('dashboard:customer')
        
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        if rating and comment:
            Testimonial.objects.create(
                customer_name=request.user.get_full_name() or request.user.username,
                customer_role='Customer',
                service=booking.service,
                content=comment,
                rating=int(rating),
                is_approved=False  # Requires admin approval
            )
            messages.success(request, 'Thank you for your feedback! It will be visible after admin approval.')
        else:
            messages.error(request, 'Please provide both rating and comment.')
    
    return redirect('dashboard:customer')