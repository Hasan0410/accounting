from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLES = [
        ('ADMIN', 'Administrator'),
        ('ACCOUNTANT', 'Accountant'),
        ('MANAGER', 'Manager'),
        ('VIEWER', 'Viewer'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLES, default='VIEWER')
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

class Contact(models.Model):
    TYPES = [('CUSTOMER', 'Customer'), ('VENDOR', 'Vendor')]
    name = models.CharField(max_length=200)
    contact_type = models.CharField(max_length=20, choices=TYPES)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.contact_type})"

class Account(models.Model):
    ACCOUNT_TYPES = [
        ('ASSET', 'Asset'),
        ('LIABILITY', 'Liability'),
        ('EQUITY', 'Equity'),
        ('REVENUE', 'Revenue'),
        ('EXPENSE', 'Expense'),
    ]

    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def balance(self):
        debits = self.lines.aggregate(Sum('debit'))['debit__sum'] or 0
        credits = self.lines.aggregate(Sum('credit'))['credit__sum'] or 0
        
        if self.account_type in ['ASSET', 'EXPENSE']:
            return debits - credits
        else:
            return credits - debits

class JournalEntry(models.Model):
    date = models.DateField()
    description = models.TextField()
    contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Journal Entries"

    def __str__(self):
        return f"Entry {self.id} - {self.date}"

class JournalEntryLine(models.Model):
    journal_entry = models.ForeignKey(JournalEntry, related_name='lines', on_delete=models.CASCADE)
    account = models.ForeignKey(Account, related_name='lines', on_delete=models.CASCADE)
    debit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.account.name} - D: {self.debit}, C: {self.credit}"

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in

class AuditLog(models.Model):
    action = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField()

    def __str__(self):
        return f"{self.timestamp} - {self.user} - {self.action}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    AuditLog.objects.create(
        action='USER_LOGIN',
        user=user,
        details=f"User {user.username} logged in from IP {request.META.get('REMOTE_ADDR')}"
    )
