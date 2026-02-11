import os
import django
import sys

# Set up Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'harry.settings')
django.setup()

from django.contrib.auth.models import User
from accounting.models import Contact, UserProfile

def seed_advanced():
    # 1. Create Contacts
    contacts_data = [
        ('Global Tech Solutions', 'VENDOR', 'billing@globaltech.com'),
        ('Office Supplies Co', 'VENDOR', 'sales@officesupplies.pk'),
        ('Acme Corp', 'CUSTOMER', 'finance@acme.com'),
        ('Hassan Mustafa', 'CUSTOMER', 'hassan@example.com'),
    ]

    for name, c_type, email in contacts_data:
        Contact.objects.get_or_create(
            name=name,
            contact_type=c_type,
            defaults={'email': email}
        )
    print("Contacts seeded.")

    # 2. Update existing users with roles
    admin_user, _ = User.objects.get_or_create(username='admin', defaults={'is_staff':True, 'is_superuser':True})
    admin_user.set_password('admin123')
    admin_user.save()
    
    # Profile check
    profile, _ = UserProfile.objects.get_or_create(user=admin_user)
    profile.role = 'ADMIN'
    profile.save()

    acc_user, _ = User.objects.get_or_create(username='accountant')
    acc_user.set_password('acc123')
    acc_user.save()
    
    profile, _ = UserProfile.objects.get_or_create(user=acc_user)
    profile.role = 'ACCOUNTANT'
    profile.save()

    print(f"Users seeded: admin/admin123 (ADMIN), accountant/acc123 (ACCOUNTANT)")

if __name__ == "__main__":
    seed_advanced()
