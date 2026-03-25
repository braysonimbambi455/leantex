from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, help_text="Font Awesome icon class", default="fa-service")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

class Service(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    duration = models.IntegerField(help_text="Duration in minutes", validators=[MinValueValidator(15)])
    image = models.ImageField(upload_to='services/', null=True, blank=True)
    is_available = models.BooleanField(default=True)
    features = models.TextField(help_text="List features separated by commas", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('services:detail', args=[str(self.id)])

    def get_features_list(self):
        if self.features:
            return [f.strip() for f in self.features.split(',') if f.strip()]
        return []

    @property
    def formatted_price(self):
        return f"KSh {self.price:,.0f}"

class Testimonial(models.Model):
    customer_name = models.CharField(max_length=100)
    customer_role = models.CharField(max_length=100, blank=True)
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True, related_name='testimonials')
    content = models.TextField()
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], default=5)
    image = models.ImageField(upload_to='testimonials/', null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.customer_name} - {self.rating} stars"