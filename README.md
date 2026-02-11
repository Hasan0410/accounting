# Harry Accounting System

A professional, feature-rich Django-based accounting and financial management platform. This system provides a robust framework for double-entry bookkeeping, financial reporting, and user movement auditing.

## 🚀 Key Features

- **📊 Comprehensive Dashboard**: Get a real-time overview of your financial status, including total balances and recent activities.
- **📔 Double-Entry Bookkeeping**: A solid foundation for accounting with automated debit/credit validation through Journal Entries.
- **📂 Chart of Accounts**: Structured management of Assets, Liabilities, Equity, Revenue, and Expenses with automatic balance calculation.
- **📈 Professional Reporting**:
  - **Profit & Loss**: Monitor your net income and expenses.
  - **Balance Sheet**: View your assets and liabilities at any point in time.
  - **Cash Flow**: Track the movement of cash within your business.
- **👥 Contact Management**: Centralized management for Customers and Vendors.
- **🛡️ Role-Based Access Control (RBAC)**: Defined roles including Admin, Accountant, Manager, and Viewer to ensure data integrity.
- **📜 Audit Logging**: Automatically tracks user logins and critical system actions for compliance and security.

## 🛠️ Technology Stack

- **Backend**: Python, Django 6.0+
- **Database**: SQLite3 (Standard Development) / PostgreSQL (Production ready)
- **Frontend**: Django Template Engine, Vanilla CSS
- **Authentication**: Django Auth System with custom User Profiles

## 📋 Prerequisites

- **Python**: 3.10 or higher
- **Django**: 6.0 or higher

## 🔧 Installation & Setup

1. **Clone or Download** the project files.
2. **Set up a Virtual Environment**:
   ```powershell
   python -m venv my_venv
   .\my_venv\Scripts\activate
   ```
3. **Install Dependencies**:
   ```powershell
   pip install django
   ```
4. **Apply Database Migrations**:
   ```powershell
   cd harry
   python manage.py migrate
   ```
5. **Seed Initial Data** (Optional but recommended for testing):
   ```powershell
   python seed_accounting.py
   python seed_advanced.py
   ```
6. **Create an Administrative User**:
   ```powershell
   python manage.py createsuperuser
   ```
7. **Start the Development Server**:
   ```powershell
   python manage.py runserver
   ```

## 📂 Project Structure

```text
accounting/
├── harry/                # Root Django Project Directory
│   ├── harry/            # Project Settings & Configuration
│   ├── accounting/       # Core Accounting Application
│   ├── manage.py         # Django Manager Script
│   └── seed_*.py         # Database Seeding Utility Scripts
├── my_venv/              # Virtual Environment
└── README.md             # Project Documentation
```

## 🔐 Security Features

- **Encrypted Passwords**: Uses Django's PBKDF2 algorithm for password hashing.
- **CSRF Protection**: Robust protection against Cross-Site Request Forgery.
- **Session-Based Auth**: Secure session management for logged-in users.

---
*Developed by Hassan Mustafa*
