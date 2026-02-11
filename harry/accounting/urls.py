from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('accounts/', views.accounts_list, name='accounts_list'),
    path('accounts/<int:account_id>/', views.account_detail, name='account_detail'),
    path('transactions/', views.transactions_list, name='transactions_list'),
    path('transactions/add/', views.add_transaction, name='add_transaction'),
    path('reports/profit-loss/', views.profit_loss_report, name='profit_loss'),
    path('reports/balance-sheet/', views.balance_sheet_report, name='balance_sheet'),
    path('reports/cash-flow/', views.cash_flow_report, name='cash_flow'),
    path('audit-logs/', views.audit_logs, name='audit_logs'),
    
    # Auth
    path('login/', auth_views.LoginView.as_view(template_name='accounting/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
