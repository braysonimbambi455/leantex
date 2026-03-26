import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'leantex.settings')
django.setup()

from django.core.management import call_command
from services.models import Service
from django.apps import apps

def load_all():
    print("=" * 50)
    print("LOADING ALL SERVICES DATA")
    print("=" * 50)
    
    # Check what models exist
    services_models = apps.get_app_config('services').get_models()
    print(f"\nFound models in services app:")
    for model in services_models:
        print(f"  - {model.__name__}")
    
    # Clear existing data (in reverse order due to foreign keys)
    print("\nClearing existing data...")
    Service.objects.all().delete()
    
    # Try to clear Category if it exists
    try:
        from services.models import Category
        Category.objects.all().delete()
        print("✓ Cleared categories")
    except ImportError:
        pass
    
    # Load data
    try:
        print("\nLoading fixtures...")
        call_command('loaddata', 'fixtures/all_services_data.json', verbosity=2)
        
        # Verify
        service_count = Service.objects.count()
        print(f"\n✓ Success! Loaded {service_count} services")
        
        # List services
        if service_count > 0:
            print("\nServices loaded:")
            for service in Service.objects.all()[:10]:
                name = service.name if hasattr(service, 'name') else str(service)
                print(f"  - {name}")
                
    except Exception as e:
        print(f"\nError: {e}")
        print("\nTrying manual import...")
        
        # Manual import alternative
        import json
        with open('fixtures/all_services_data.json', 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
        
        # First create categories
        categories = {}
        for item in data:
            if 'category' in item['model'].lower():
                if 'services.category' in item['model']:
                    from services.models import Category
                    cat = Category.objects.create(**item['fields'])
                    categories[item['pk']] = cat
                    print(f"  Created category: {cat.name if hasattr(cat, 'name') else cat}")
        
        # Then create services
        for item in data:
            if 'services.service' in item['model']:
                fields = item['fields'].copy()
                # Convert category ID to Category instance
                if 'category' in fields and fields['category'] in categories:
                    fields['category'] = categories[fields['category']]
                Service.objects.create(**fields)
                print(f"  Created service: {fields.get('name', 'Unknown')}")
        
        print(f"\n✓ Loaded {Service.objects.count()} services manually!")

if __name__ == '__main__':
    load_all()