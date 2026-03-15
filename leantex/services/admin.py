from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Service, Testimonial

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'service_count', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'name': ('name',)}
    
    def service_count(self, obj):
        return obj.services.count()
    service_count.short_description = 'Number of Services'

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'display_price', 'duration', 'is_available', 'booking_count', 'image_preview']
    list_filter = ['category', 'is_available', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_available']
    readonly_fields = ['image_preview', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('category', 'name', 'description', 'price', 'duration')
        }),
        ('Media', {
            'fields': ('image', 'image_preview'),
            'classes': ('wide',)
        }),
        ('Details', {
            'fields': ('features', 'is_available')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def display_price(self, obj):
        return obj.formatted_price
    display_price.short_description = 'Price'
    display_price.admin_order_field = 'price'
    
    def booking_count(self, obj):
        count = obj.bookings.count()
        return format_html('<b>{}</b>', count)
    booking_count.short_description = 'Bookings'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Preview'

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['customer_name', 'service', 'rating', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'rating', 'service']
    search_fields = ['customer_name', 'content']
    list_editable = ['is_approved']
    actions = ['approve_testimonials']
    
    def approve_testimonials(self, request, queryset):
        queryset.update(is_approved=True)
    approve_testimonials.short_description = "Approve selected testimonials"