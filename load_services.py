import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'leantex.settings')
django.setup()

from django.core.management import call_command
from services.models import Service

# Clear existing services
Service.objects.all().delete()
print(f"Cleared existing services")

# Load new data
call_command('loaddata', 'fixtures/services_complete.json')
print(f"Loaded {Service.objects.count()} services successfully!")