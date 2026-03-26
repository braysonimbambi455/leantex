import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'leantex.settings')
django.setup()

from django.core.management import call_command
from django.contrib.auth.models import User

def load_data():
    print("Loading data from fixtures/app_data.json...")
    
    try:
        # Load the data
        call_command('loaddata', 'fixtures/app_data.json')
        print("Data loaded successfully!")
        
        # Optional: Print summary
        from services.models import Service
        from bookings.models import Booking
        from accounts.models import Profile  # Adjust based on your models
        
        print(f"\nData Summary:")
        print(f"Services: {Service.objects.count()}")
        print(f"Bookings: {Booking.objects.count()}")
        
    except Exception as e:
        print(f"Error loading data: {e}")

if __name__ == '__main__':
    load_data()