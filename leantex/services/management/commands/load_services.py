from django.core.management.base import BaseCommand
from services.models import Category, Service
from django.core.files import File
from pathlib import Path
import os
import requests
from io import BytesIO

class Command(BaseCommand):
    help = 'Load initial services with images'

    def handle(self, *args, **kwargs):
        self.stdout.write('Loading services...')
        
        # Create categories first
        categories = [
            {'name': 'CCTV Installation', 'icon': 'fa-video', 'description': 'Professional security camera installation services for home and business'},
            {'name': 'WiFi Setup', 'icon': 'fa-wifi', 'description': 'Wireless network installation and configuration services'},
            {'name': 'Accounting Advice', 'icon': 'fa-calculator', 'description': 'Financial and accounting advisory services for businesses'},
            {'name': 'Computer Sales', 'icon': 'fa-laptop', 'description': 'New and refurbished computers, laptops, and accessories'},
            {'name': 'Laptop Repair', 'icon': 'fa-tools', 'description': 'Professional laptop repair and maintenance services'},
        ]
        
        created_categories = {}
        for cat_data in categories:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'icon': cat_data['icon'],
                    'description': cat_data['description']
                }
            )
            created_categories[cat_data['name']] = category
            self.stdout.write(f'  {"Created" if created else "Found"} category: {category.name}')

        # Services data with image URLs
        services_data = [
            # CCTV Installation Services
            {
                'category': 'CCTV Installation',
                'name': 'Home CCTV Installation - 4 Camera System',
              'description': 'Complete home security solution with 4 high-definition cameras, DVR with 1TB storage, and professional installation. Includes remote viewing via smartphone and 1-year warranty.',
                'price': 25000,
                'duration': 180,
                'features': '4 HD 1080p cameras,DVR with 1TB storage,Remote viewing app,Professional installation,1 year warranty,Night vision capability,Motion detection,Smartphone alerts',
                'image_url': 'https://images.pexels.com/photos/3961311/pexels-photo-3961311.jpeg?auto=compress&cs=tinysrgb&w=800',
                'is_available': True
            },
            {
                'category': 'CCTV Installation',
                'name': 'Business CCTV System - 8 Camera',
                'description': 'Commercial-grade security system with 8 cameras, NVR with 2TB storage, and advanced features. Perfect for offices, shops, and warehouses.',
                'price': 45000,
                'duration': 240,
                'features': '8 HD 1080p cameras,NVR with 2TB storage,Remote viewing,2 years warranty,24/7 support,Advanced motion detection,Multi-user access,Cloud backup option',
                'image_url': 'https://images.unsplash.com/photo-1558005530-a7958896ec60?w=800',
                'is_available': True
            },
            {
                'category': 'CCTV Installation',
                'name': 'PTZ Camera System',
                'description': 'Professional PTZ (Pan-Tilt-Zoom) camera system with 360° coverage. Ideal for large spaces and areas requiring detailed monitoring.',
                'price': 65000,
                'duration': 300,
                'features': 'PTZ camera with 360° coverage,30x optical zoom,NVR with 3TB storage,Remote control,Advanced tracking,2 years warranty,Professional installation',
                'image_url': 'https://images.unsplash.com/photo-1563013544-824ae1b704d3?w=800',
                'is_available': True
            },
            {
                'category': 'CCTV Installation',
                'name': 'Wireless CCTV System',
                'description': 'Easy-to-install wireless security cameras with battery backup. Perfect for rentals or places where wiring is difficult.',
                'price': 35000,
                'duration': 150,
                'features': '4 wireless cameras,Cloud storage,2-way audio,Battery backup,Smart home integration,Free mobile app,6 months warranty',
                'image_url': 'https://images.unsplash.com/photo-1585506942812-e72b29cef752?w=800',
                'is_available': True
            },
            
            # WiFi Setup Services
            {
                'category': 'WiFi Setup',
                'name': 'Home WiFi Installation',
                'description': 'Professional WiFi setup for homes with optimal coverage. Includes router configuration, security setup, and device connection assistance.',
                'price': 5000,
                'duration': 60,
                'features': 'Router configuration,Network security setup,WiFi optimization,Device connection (up to 5 devices),Guest network setup,1 month support',
                'image_url': 'https://images.unsplash.com/photo-1563986768609-322da13575f3?w=800',
                'is_available': True
            },
            {
                'category': 'WiFi Setup',
                'name': 'Office Network Setup',
                'description': 'Complete office network infrastructure setup with multiple access points, VLAN configuration, and enterprise-grade security.',
                'price': 15000,
                'duration': 180,
                'features': 'Multiple access points,VLAN configuration,Firewall setup,Network security,Server room setup,60+ device capacity,6 months support',
                'image_url': 'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=800',
                'is_available': True
            },
            {
                'category': 'WiFi Setup',
                'name': 'Outdoor WiFi Extension',
                'description': 'Extend your WiFi coverage to outdoor areas like gardens, patios, and pool areas with weatherproof access points.',
                'price': 12000,
                'duration': 90,
                'features': 'Weatherproof access point,300m range,PoE support,Outdoor rated cabling,2 years warranty',
                'image_url': 'https://images.unsplash.com/photo-1625842268584-8f3296236761?w=800',
                'is_available': True
            },
            
            # Accounting Advice Services
            {
                'category': 'Accounting Advice',
                'name': 'Business Tax Consultation',
                'description': 'Expert tax advice for small businesses. Includes tax planning, compliance review, and filing assistance.',
                'price': 3000,
                'duration': 60,
                'features': 'Tax planning,Compliance review,KRA filing assistance,Deduction optimization,Financial advice,Follow-up consultation',
                'image_url': 'https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=800',
                'is_available': True
            },
            {
                'category': 'Accounting Advice',
                'name': 'Bookkeeping Setup',
                'description': 'Professional bookkeeping system setup for businesses. Includes software setup, training, and monthly reconciliation.',
                'price': 8000,
                'duration': 120,
                'features': 'Software setup (QuickBooks),Staff training,Monthly reconciliation,Financial reports,Tax preparation assistance,1 month support',
                'image_url': 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800',
                'is_available': True
            },
            {
                'category': 'Accounting Advice',
                'name': 'Financial Audit Preparation',
                'description': 'Prepare your business for financial audit with expert guidance and documentation review.',
                'price': 5000,
                'duration': 90,
                'features': 'Document review,Audit checklist,Financial statement prep,Compliance check,Corrective actions,Audit support',
                'image_url': 'https://images.unsplash.com/photo-1554224154-26032ffc0d07?w=800',
                'is_available': True
            },
            {
                'category': 'Accounting Advice',
                'name': 'Startup Financial Planning',
                'description': 'Comprehensive financial planning for startups. Includes budgeting, forecasting, and investor-ready reports.',
                'price': 6000,
                'duration': 90,
                'features': 'Business plan financials,Cash flow forecasting,Budgeting,Investor reports,Financial modeling,2 follow-up sessions',
                'image_url': 'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=800',
                'is_available': True
            },
            
            # Computer Sales
            {
                'category': 'Computer Sales',
                'name': 'Business Desktop Computer',
                'description': 'High-performance desktop computer for business use. Perfect for office work, accounting, and general business applications.',
                'price': 45000,
                'duration': 30,
                'features': 'Intel Core i7,16GB RAM,512GB SSD,Windows 11 Pro,24" monitor,Keyboard & mouse,1 year warranty,Free setup',
                'image_url': 'https://images.unsplash.com/photo-1587831990711-23ca6441447b?w=800',
                'is_available': True
            },
            {
                'category': 'Computer Sales',
                'name': 'Gaming Laptop',
                'description': 'High-performance gaming laptop with dedicated graphics. Perfect for gaming, video editing, and demanding applications.',
                'price': 85000,
                'duration': 30,
                'features': 'Intel Core i7,16GB RAM,512GB SSD,NVIDIA RTX 3060,15.6" 144Hz display,RGB keyboard,2 years warranty,Gaming mouse included',
                'image_url': 'https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=800',
                'is_available': True
            },
            {
                'category': 'Computer Sales',
                'name': 'All-in-One Desktop',
              'description': 'Space-saving all-in-one desktop computer. Perfect for home offices, reception areas, and general use.',
                'price': 55000,
                'duration': 30,
                'features': 'Intel Core i5,8GB RAM,256GB SSD,23.8" touch screen,Windows 11 Home,Wireless keyboard & mouse,1 year warranty',
                'image_url': 'https://images.pexels.com/photos/1029757/pexels-photo-1029757.jpeg?auto=compress&cs=tinysrgb&w=800',
                'is_available': True
            },
            {
                'category': 'Computer Sales',
                'name': 'Budget Desktop Computer',
                'description': 'Affordable desktop computer for basic tasks like browsing, documents, and emails. Great for students and home use.',
                'price': 25000,
                'duration': 30,
                'features': 'Intel Core i3,8GB RAM,256GB SSD,Windows 11 Home,19" monitor,Keyboard & mouse,6 months warranty',
                'image_url': 'https://images.unsplash.com/photo-1593640408182-31c70c8268f5?w=800',
                'is_available': True
            },
            {
                'category': 'Computer Sales',
                'name': 'MacBook Pro',
                'description': 'Apple MacBook Pro with M2 chip. Perfect for creative professionals, developers, and power users.',
                'price': 165000,
                'duration': 30,
                'features': 'Apple M2 chip,16GB RAM,512GB SSD,13.3" Retina display,Touch ID,2 years warranty,Free accessories',
                'image_url': 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800',
                'is_available': True
            },
            
            # Laptop Repair Services
            {
                'category': 'Laptop Repair',
                'name': 'Screen Replacement',
                'description': 'Professional laptop screen replacement service for all major brands. High-quality replacement screens with warranty.',
                'price': 8000,
                'duration': 120,
                'features': 'Genuine replacement parts,Color calibration,Free diagnosis,3 months warranty,Quality guarantee,Same-day service',
                'image_url': 'https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?w=800',
                'is_available': True
            },
            {
                'category': 'Laptop Repair',
                'name': 'Battery Replacement',
                'description': 'Laptop battery replacement service. Original and OEM batteries available for all major laptop brands.',
                'price': 3500,
                'duration': 45,
                'features': 'Original/OEM batteries,Battery calibration,6 months warranty,Testing included,Free installation',
                'image_url': 'https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=800',
                'is_available': True
            },
            {
                'category': 'Laptop Repair',
                'name': 'Keyboard Replacement',
                'description': 'Professional laptop keyboard replacement. Fix sticky or non-working keys with quality replacement keyboards.',
                'price': 4500,
                'duration': 60,
                'features': 'Genuine replacement keyboard,Backlit option available,1 month warranty,Key testing,Free diagnosis',
                'image_url': 'https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=800',
                'is_available': True
            },
            {
                'category': 'Laptop Repair',
                'name': 'Hard Drive Upgrade to SSD',
                'description': 'Upgrade your slow hard drive to a fast SSD. Includes data transfer and fresh Windows installation.',
                'price': 6000,
                'duration': 90,
                'features': '256GB/512GB SSD options,Data transfer,OS installation,1 year warranty on SSD,System optimization,Free data backup',
                'image_url': 'https://images.unsplash.com/photo-1597852074816-d933c7d2b988?w=800',
                'is_available': True
            },
            {
                'category': 'Laptop Repair',
                'name': 'Virus Removal & System Cleanup',
                'description': 'Complete virus removal and system optimization. Make your laptop run like new again.',
                'price': 2000,
                'duration': 60,
                'features': 'Full virus scan,Malware removal,System optimization,Startup cleanup,Temporary file cleanup,3 months protection',
                'image_url': 'https://images.unsplash.com/photo-1585060544812-6b45742d762f?w=800',
                'is_available': True
            },
            {
                'category': 'Laptop Repair',
                'name': 'Water Damage Repair',
                'description': 'Emergency water damage repair service. Quick response to save your laptop from liquid damage.',
                'price': 5000,
                'duration': 180,
                'features': 'Emergency service,Component cleaning,Corrosion treatment,Testing,1 month warranty,Free diagnosis',
                'image_url': 'https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=800',
                'is_available': True
            },
            {
                'category': 'Laptop Repair',
                'name': 'Charging Port Repair',
                'description': 'Fix broken or loose charging ports. Get your laptop charging properly again.',
                'price': 3000,
                'duration': 60,
                'features': 'Port replacement,Soldering repair,Charging test,1 month warranty,Quick service',
                'image_url': 'https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=800',
                'is_available': True
            },
        ]

        # Create services
        for service_data in services_data:
            category_name = service_data.pop('category')
            category = created_categories[category_name]
            
            # Get or create service
            service, created = Service.objects.get_or_create(
                name=service_data['name'],
                defaults={
                    'category': category,
                    'description': service_data['description'],
                    'price': service_data['price'],
                    'duration': service_data['duration'],
                    'features': service_data['features'],
                    'is_available': service_data.get('is_available', True),
                }
            )
            
            # Download and save image
            if created and service_data.get('image_url'):
                try:
                    response = requests.get(service_data['image_url'])
                    if response.status_code == 200:
                        img_temp = BytesIO(response.content)
                        service.image.save(
                            f"{service.name.lower().replace(' ', '_')}.jpg",
                            File(img_temp),
                            save=True
                        )
                        self.stdout.write(f'  ✅ Created service with image: {service.name}')
                    else:
                        self.stdout.write(f'  ⚠️ Created service (image download failed): {service.name}')
                except Exception as e:
                    self.stdout.write(f'  ⚠️ Created service (image error: {str(e)}): {service.name}')
            elif not created:
                self.stdout.write(f'  📦 Found existing service: {service.name}')
            else:
                self.stdout.write(f'  ✅ Created service (no image): {service.name}')

        self.stdout.write(self.style.SUCCESS(f'Successfully loaded {len(services_data)} services'))