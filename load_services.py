import os
import sys
import json
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'leantex.settings')
django.setup()

from django.core.management import call_command
from services.models import Service

def load_services():
    print("Clearing existing services...")
    Service.objects.all().delete()
    print("✓ Cleared")
    
    try:
        print("Loading services...")
        # Try to load the fixture
        call_command('loaddata', 'fixtures/services_complete.json', verbosity=2)
        count = Service.objects.count()
        print(f"✓ Successfully loaded {count} services!")
        
        # List loaded services
        if count > 0:
            print("\nServices in database:")
            for service in Service.objects.all():
                print(f"  - {service.name if hasattr(service, 'name') else service}")
                
    except Exception as e:
        print(f"Error: {e}")
        print("\nTrying alternative method...")
        
        # Alternative: manual JSON load
        try:
            with open('fixtures/services_complete.json', 'r', encoding='utf-8-sig') as f:  # utf-8-sig removes BOM
                data = json.load(f)
            
            for item in data:
                if item['model'] == 'services.service':
                    # Create service from JSON
                    service = Service.objects.create(**item['fields'])
                    print(f"  Created: {service.name if hasattr(service, 'name') else service}")
            
            count = Service.objects.count()
            print(f"\n✓ Loaded {count} services manually!")
            
        except Exception as e2:
            print(f"Alternative method also failed: {e2}")

if __name__ == '__main__':
    load_services()