# Create this file in your leantex folder (same folder as settings.py)

from django.http import HttpResponse
from django.contrib.auth.models import User
from accounts.models import Profile

def create_admin(request):
    """Temporary view to create admin - DELETE AFTER USE"""
    try:
        # Check if admin exists
        if User.objects.filter(username='admin').exists():
            return HttpResponse("Admin user already exists!<br>Username: admin<br>Password: admin123")
        
        # Create superuser
        admin = User.objects.create_superuser(
            username='admin',
            email='braysonimbambi455@gmail.com',
            password='admin123',
            first_name='System',
            last_name='Administrator'
        )
        
        # Create profile
        profile, created = Profile.objects.get_or_create(user=admin)
        profile.phone_number = '+254793814747'
        profile.role = 'admin'
        profile.address = 'Nairobi'
        profile.city = 'Nairobi'
        profile.save()
        
        return HttpResponse("""
        <h1>✅ Admin Created Successfully!</h1>
        <p><strong>Username:</strong> admin</p>
        <p><strong>Password:</strong> admin123</p>
        <p><a href="/admin/">Click here to login to admin panel</a></p>
        <hr>
        <p style="color:red;"><strong>IMPORTANT:</strong> After you login, delete this file or remove this URL!</p>
        """)
        
    except Exception as e:
        return HttpResponse(f"<h1>Error creating admin</h1><p>{e}</p>")