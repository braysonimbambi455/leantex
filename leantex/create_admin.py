from django.http import HttpResponse
from django.contrib.auth.models import User
from accounts.models import Profile

def create_admin(request):
    """Temporary view to create admin - DELETE AFTER USE"""
    
    response_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Create Admin - Leantex</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #f0f8ff; }
            .container { background: white; padding: 30px; border-radius: 10px; max-width: 500px; margin: auto; box-shadow: 0 3px 10px rgba(0,0,0,0.1); }
            h2 { color: #0d6efd; }
            .success { color: green; }
            .error { color: red; }
            code { background: #f4f4f4; padding: 2px 5px; border-radius: 3px; }
            .btn { display: inline-block; background: #0d6efd; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-top: 20px; }
            .info { text-align: left; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
    """
    
    try:
        # Check if admin already exists
        if User.objects.filter(username='admin455').exists():
            admin = User.objects.get(username='admin455')
            response_html += f"""
                <h2>⚠️ Admin Already Exists</h2>
                <div class="info">
                    <p><strong>Username:</strong> <code>admin455</code></p>
                    <p><strong>Password:</strong> <code>cmfbrayden455</code></p>
                    <p><strong>Email:</strong> braysonimbambi455@gmail.com</p>
                    <p><strong>Superuser:</strong> {admin.is_superuser}</p>
                    <p><strong>Staff:</strong> {admin.is_staff}</p>
                </div>
                <a href="/admin/" class="btn">Go to Admin Panel →</a>
            """
        else:
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
            profile.phone_number = '+254700000000'
            profile.role = 'admin'
            profile.address = 'Nairobi'
            profile.city = 'Nairobi'
            profile.save()
            
            response_html += f"""
                <h2 class="success">✅ Admin Created Successfully!</h2>
                <div class="info">
                    <p><strong>Username:</strong> <code>admin455</code></p>
                    <p><strong>Password:</strong> <code>cmfbrayden455</code></p>
                    <p><strong>Email:</strong> braysonimbambi455@gmail.com</p>
                </div>
                <a href="/admin/" class="btn">Login to Admin Panel →</a>
                <p style="margin-top: 20px; font-size: 12px; color: #999;">After logging in, remove this view from urls.py</p>
            """
            
    except Exception as e:
        response_html += f"""
            <h2 class="error">❌ Error Creating Admin</h2>
            <div class="info">
                <p>Error: {str(e)}</p>
            </div>
        """
    
    response_html += """
        </div>
    </body>
    </html>
    """
    
    return HttpResponse(response_html)