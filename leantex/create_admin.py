from django.http import HttpResponse
from django.contrib.auth.models import User
from accounts.models import Profile

def create_admin(request):
    """Temporary view to create admin - DELETE AFTER USE"""
    try:
        # Check if admin already exists
        if User.objects.filter(username='admin455').exists():
            return HttpResponse("""
            <html>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h2>⚠️ Admin Already Exists</h2>
                <p>Username: admin455</p>
                <p>Password: cmfbrayden455</p>
                <a href="/admin/">Go to Admin Panel</a>
            </body>
            </html>
            """)
        
        # Create superuser
        admin = User.objects.create_superuser(
            username='admin455',
            email='braysonimbambi455@gmail.com',
            password='cmfbrayden455',
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
        <html>
        <body style="font-family: Arial; text-align: center; padding: 50px; background: #f0f8ff;">
            <div style="background: white; padding: 30px; border-radius: 10px; max-width: 500px; margin: auto; box-shadow: 0 3px 10px rgba(0,0,0,0.1);">
                <h2 style="color: green;">✅ Admin Created Successfully!</h2>
                <div style="text-align: left; margin: 20px 0;">
                    <p><strong>Username:</strong> <code>admin455</code></p>
                    <p><strong>Password:</strong> <code>cmfbrayden455</code></p>
                    <p><strong>Email:</strong> braysonimbambi455@gmail.com</p>
                </div>
                <div style="margin-top: 20px;">
                    <a href="/admin/" style="background: #0d6efd; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Login to Admin Panel →</a>
                </div>
                <p style="margin-top: 20px; font-size: 12px; color: #999;">After logging in, remove this view from urls.py</p>
            </div>
        </body>
        </html>
        """)
        
    except Exception as e:
        return HttpResponse(f"""
        <html>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h2 style="color: red;">❌ Error Creating Admin</h2>
            <p>{e}</p>
        </body>
        </html>
        """)