from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .models import Account, JournalEntry, JournalEntryLine, Contact, AuditLog, UserProfile
from datetime import date, timedelta

@login_required
def dashboard(request):
    # Optimized account fetching
    accounts = Account.objects.all()
    total_assets = sum(a.balance for a in accounts if a.account_type == 'ASSET')
    total_liabilities = sum(a.balance for a in accounts if a.account_type == 'LIABILITY')
    total_equity = sum(a.balance for a in accounts if a.account_type == 'EQUITY')
    
    today = date.today()
    start_of_month = today.replace(day=1)
    
    # Efficient aggregation
    monthly_stats = JournalEntryLine.objects.filter(
        journal_entry__date__gte=start_of_month
    ).select_related('account')
    
    monthly_revenue = monthly_stats.filter(account__account_type='REVENUE').aggregate(Sum('credit'))['credit__sum'] or 0
    monthly_expense = monthly_stats.filter(account__account_type='EXPENSE').aggregate(Sum('debit'))['debit__sum'] or 0
    net_income = monthly_revenue - monthly_expense

    # Recent Activity for extra dashboard feature
    recent_transactions = JournalEntry.objects.all().select_related('created_by').order_by('-created_at')[:5]

    # Chart Data (Last 6 Months)
    chart_labels = []
    revenue_data = []
    expense_data = []
    
    for i in range(5, -1, -1):
        month_date = today - timedelta(days=i*30)
        chart_labels.append(month_date.strftime('%b'))
        
        m_start = month_date.replace(day=1)
        if month_date.month == 12:
            m_end = month_date.replace(year=month_date.year+1, month=1, day=1) - timedelta(days=1)
        else:
            m_end = month_date.replace(month=month_date.month+1, day=1) - timedelta(days=1)
            
        rev = JournalEntryLine.objects.filter(
            account__account_type='REVENUE',
            journal_entry__date__range=[m_start, m_end]
        ).aggregate(Sum('credit'))['credit__sum'] or 0
        
        exp = JournalEntryLine.objects.filter(
            account__account_type='EXPENSE',
            journal_entry__date__range=[m_start, m_end]
        ).aggregate(Sum('debit'))['debit__sum'] or 0
        
        revenue_data.append(float(rev))
        expense_data.append(float(exp))

    context = {
        'total_assets': total_assets,
        'total_liabilities': total_liabilities,
        'total_equity': total_equity,
        'monthly_revenue': monthly_revenue,
        'monthly_expense': monthly_expense,
        'net_income': net_income,
        'chart_labels': chart_labels,
        'revenue_data': revenue_data,
        'expense_data': expense_data,
        'recent_transactions': recent_transactions,
    }
    return render(request, 'accounting/dashboard.html', context)

@login_required
def accounts_list(request):
    accounts = Account.objects.all().order_by('code')
    return render(request, 'accounting/accounts_list.html', {'accounts': accounts})

@login_required
def account_detail(request, account_id):
    account = get_object_or_404(Account, id=account_id)
    lines = JournalEntryLine.objects.filter(account=account).select_related('journal_entry').order_by('-journal_entry__date')
    
    # Simple running balance calculation
    balance = 0
    for line in reversed(list(lines)):
        if account.account_type in ['ASSET', 'EXPENSE']:
            balance += (line.debit - line.credit)
        else:
            balance += (line.credit - line.debit)
        line.running_balance = balance

    return render(request, 'accounting/account_detail.html', {
        'account': account,
        'lines': lines,
    })

@login_required
def transactions_list(request):
    entries = JournalEntry.objects.all().select_related('contact', 'created_by').prefetch_related('lines__account').order_by('-date', '-created_at')
    
    # Simple Filtering
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date:
        entries = entries.filter(date__gte=start_date)
    if end_date:
        entries = entries.filter(date__lte=end_date)
        
    return render(request, 'accounting/transactions_list.html', {
        'entries': entries,
        'start_date': start_date,
        'end_date': end_date
    })

@login_required
def add_transaction(request):
    if request.method == 'POST':
        description = request.POST.get('description')
        entry_date = request.POST.get('date')
        contact_id = request.POST.get('contact')
        
        contact = None
        if contact_id:
            contact = Contact.objects.get(id=contact_id)
            
        entry = JournalEntry.objects.create(
            date=entry_date, 
            description=description,
            contact=contact,
            created_by=request.user
        )
        
        acc_debit_id = request.POST.get('debit_account')
        amount_debit = request.POST.get('debit_amount')
        acc_credit_id = request.POST.get('credit_account')
        amount_credit = request.POST.get('credit_amount')
        
        if acc_debit_id and amount_debit:
            JournalEntryLine.objects.create(journal_entry=entry, account_id=acc_debit_id, debit=amount_debit)
        if acc_credit_id and amount_credit:
            JournalEntryLine.objects.create(journal_entry=entry, account_id=acc_credit_id, credit=amount_credit)
        
        # Log action
        AuditLog.objects.create(
            action='CREATE_TRANSACTION',
            user=request.user,
            details=f"Created journal entry #{entry.id}: {description}"
        )
            
        return redirect('transactions_list')
        
    accounts = Account.objects.all()
    contacts = Contact.objects.all()
    return render(request, 'accounting/add_transaction.html', {
        'accounts': accounts, 
        'contacts': contacts,
        'today': date.today()
    })

@login_required
def profit_loss_report(request):
    # This report covers current year
    year = date.today().year
    revenue_accounts = Account.objects.filter(account_type='REVENUE')
    expense_accounts = Account.objects.filter(account_type='EXPENSE')
    
    # Calculate balances for each account
    for acc in revenue_accounts:
        acc.current_balance = acc.balance
    for acc in expense_accounts:
        acc.current_balance = acc.balance
        
    total_revenue = sum(acc.balance for acc in revenue_accounts)
    total_expense = sum(acc.balance for acc in expense_accounts)
    net_profit = total_revenue - total_expense
    
    return render(request, 'accounting/reports/profit_loss.html', {
        'revenue_accounts': revenue_accounts,
        'expense_accounts': expense_accounts,
        'total_revenue': total_revenue,
        'total_expense': total_expense,
        'net_profit': net_profit,
        'year': year
    })

@login_required
def balance_sheet_report(request):
    assets = Account.objects.filter(account_type='ASSET')
    liabilities = Account.objects.filter(account_type='LIABILITY')
    equity = Account.objects.filter(account_type='EQUITY')
    
    total_assets = sum(a.balance for a in assets)
    total_liabilities = sum(a.balance for a in liabilities)
    total_equity = sum(a.balance for a in equity)
    
    return render(request, 'accounting/reports/balance_sheet.html', {
        'assets': assets,
        'liabilities': liabilities,
        'equity': equity,
        'total_assets': total_assets,
        'total_liabilities': total_liabilities,
        'total_equity': total_equity,
        'as_of_date': date.today()
    })

@login_required
def cash_flow_report(request):
    # Operating activities typically involve Cash/Bank accounts and Income Statement accounts
    cash_accounts = Account.objects.filter(code__startswith='10') # Simplified for demo
    
    today = date.today()
    start_of_year = today.replace(month=1, day=1)
    
    # Calculate inflows (Revenue related bank entries)
    inflows = JournalEntryLine.objects.filter(
        account__in=cash_accounts,
        debit__gt=0,
        journal_entry__date__gte=start_of_year
    ).aggregate(Sum('debit'))['debit__sum'] or 0
    
    # Calculate outflows (Expense/Asset related bank entries)
    outflows = JournalEntryLine.objects.filter(
        account__in=cash_accounts,
        credit__gt=0,
        journal_entry__date__gte=start_of_year
    ).aggregate(Sum('credit'))['credit__sum'] or 0
    
    net_cash_flow = inflows - outflows

    return render(request, 'accounting/reports/cash_flow.html', {
        'inflows': inflows,
        'outflows': outflows,
        'net_cash_flow': net_cash_flow,
        'year': today.year
    })

@staff_member_required
def audit_logs(request):
    logs = AuditLog.objects.all().order_by('-timestamp')
    return render(request, 'accounting/audit_logs.html', {'logs': logs})
