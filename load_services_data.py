import os
import sys
import json
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'leantex.settings')
django.setup()

from services.models import Category, Service, Testimonial

def load_data():
    print("\n" + "="*60)
    print("LOADING SERVICES DATA")
    print("="*60)
    
    # Clear existing data in correct order
    print("\nClearing existing data...")
    Testimonial.objects.all().delete()
    Service.objects.all().delete()
    Category.objects.all().delete()
    print("✓ Cleared existing data")
    
    # Load the JSON file
    json_path = 'fixtures/all_services_data.json'
    
    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found!")
        return
    
    try:
        # Read JSON with utf-8-sig to handle BOM
        with open(json_path, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
        
        print(f"\nFound {len(data)} objects in JSON file")
        
        # Create a dictionary to store created objects
        created_objects = {}
        
        # First pass: Create categories
        print("\nCreating categories...")
        category_count = 0
        for item in data:
            if item['model'] == 'services.category':
                obj = Category.objects.create(**item['fields'])
                created_objects[item['pk']] = obj
                category_count += 1
                name = obj.name if hasattr(obj, 'name') else str(obj)
                print(f"  ✓ Created category: {name}")
        
        print(f"Created {category_count} categories")
        
        # Second pass: Create services
        print("\nCreating services...")
        service_count = 0
        for item in data:
            if item['model'] == 'services.service':
                fields = item['fields'].copy()
                # Convert category foreign key if it exists
                if 'category' in fields and fields['category']:
                    if fields['category'] in created_objects:
                        fields['category'] = created_objects[fields['category']]
                    else:
                        fields['category'] = None
                obj = Service.objects.create(**fields)
                service_count += 1
                name = obj.name if hasattr(obj, 'name') else str(obj)
                print(f"  ✓ Created service: {name}")
        
        print(f"Created {service_count} services")
        
        # Third pass: Create testimonials if they exist
        testimonial_count = 0
        testimonial_items = [item for item in data if item['model'] == 'services.testimonial']
        if testimonial_items:
            print("\nCreating testimonials...")
            for item in testimonial_items:
                fields = item['fields'].copy()
                Testimonial.objects.create(**fields)
                testimonial_count += 1
                print(f"  ✓ Created testimonial")
            print(f"Created {testimonial_count} testimonials")
        
        # Summary
        print("\n" + "="*60)
        print("DATA LOAD COMPLETE!")
        print("="*60)
        print(f"Categories: {Category.objects.count()}")
        print(f"Services: {Service.objects.count()}")
        print(f"Testimonials: {Testimonial.objects.count()}")
        print("="*60)
        
        # List services for verification
        if Service.objects.count() > 0:
            print("\nServices loaded:")
            for service in Service.objects.all()[:10]:
                name = service.name if hasattr(service, 'name') else str(service)
                print(f"  • {name}")
            if Service.objects.count() > 10:
                print(f"  ... and {Service.objects.count() - 10} more")
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    load_data()