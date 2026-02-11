import os
import django
import sys
from datetime import date, timedelta
import random

# Set up Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'harry.settings')
django.setup()

from accounting.models import Account, JournalEntry, JournalEntryLine

def seed_data():
    # 1. Create Chart of Accounts
    accounts_data = [
        ('1000', 'Cash on Hand', 'ASSET'),
        ('1010', 'Bank Account', 'ASSET'),
        ('1020', 'Accounts Receivable', 'ASSET'),
        ('1200', 'Inventory', 'ASSET'),
        ('2000', 'Accounts Payable', 'LIABILITY'),
        ('2100', 'Sales Tax Payable', 'LIABILITY'),
        ('3000', 'Owner Capital', 'EQUITY'),
        ('4000', 'Sales Revenue', 'REVENUE'),
        ('4100', 'Service Revenue', 'REVENUE'),
        ('5020', 'Rent Expense', 'EXPENSE'),
        ('5030', 'Utility Expense', 'EXPENSE'),
        ('5040', 'Salary Expense', 'EXPENSE'),
    ]

    accounts = {}
    for code, name, acc_type in accounts_data:
        acc, created = Account.objects.get_or_create(
            code=code,
            defaults={'name': name, 'account_type': acc_type}
        )
        accounts[code] = acc
        if created:
            print(f"Created account: {name}")

    # 2. Add some transactions if none exist
    if JournalEntry.objects.count() == 0:
        print("Seeding dummy transactions...")
        
        # Initial Investment
        entry1 = JournalEntry.objects.create(date=date.today() - timedelta(days=30), description="Initial Investment")
        JournalEntryLine.objects.create(journal_entry=entry1, account=accounts['1010'], debit=50000)
        JournalEntryLine.objects.create(journal_entry=entry1, account=accounts['3000'], credit=50000)

        # Sales Revenue
        for i in range(15):
            entry_date = date.today() - timedelta(days=random.randint(1, 28))
            amount = random.randint(500, 5000)
            entry = JournalEntry.objects.create(date=entry_date, description=f"Sale #{i+1}")
            JournalEntryLine.objects.create(journal_entry=entry, account=accounts['1010'], debit=amount)
            JournalEntryLine.objects.create(journal_entry=entry, account=accounts['4000'], credit=amount)

        # Expenses
        expenses = [('5020', 2000, "Monthly Rent"), ('5030', 500, "Electricity Bill"), ('5040', 10000, "Employee Salaries")]
        for code, amount, desc in expenses:
            entry = JournalEntry.objects.create(date=date.today() - timedelta(days=5), description=desc)
            JournalEntryLine.objects.create(journal_entry=entry, account=accounts[code], debit=amount)
            JournalEntryLine.objects.create(journal_entry=entry, account=accounts['1010'], credit=amount)

        print("Transactions seeded.")

if __name__ == "__main__":
    seed_data()
