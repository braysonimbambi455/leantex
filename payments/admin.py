from django.contrib import admin
from .models import Payment, Invoice

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'booking', 'customer', 'amount', 'payment_method', 'status', 'payment_date']
    list_filter = ['status', 'payment_method', 'payment_date']
    search_fields = ['booking__booking_number', 'customer__username', 'transaction_id']
    readonly_fields = ['payment_date', 'last_updated']
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('booking', 'customer', 'amount', 'payment_method', 'status')
        }),
        ('Transaction Details', {
            'fields': ('transaction_id', 'payment_data')
        }),
        ('Timestamps', {
            'fields': ('payment_date', 'last_updated'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'payment', 'generated_at']
    search_fields = ['invoice_number']