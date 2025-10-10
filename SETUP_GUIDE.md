<!-- ============================================================================
SETUP_GUIDE.md - Comprehensive Setup Guide
============================================================================ -->

# Family Budget App - Complete Setup Guide

## Quick Start (5 minutes)

### Step 1: Clone & Setup
```bash
git clone https://github.com/yourusername/family-budget-app.git
cd family-budget-app
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Initialize Database
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### Step 3: Run Server
```bash
python manage.py runserver
```

Visit `http://localhost:8000/`

---

## Detailed Setup Instructions

### Prerequisites
- Python 3.8+
- pip
- Virtual environment (recommended)
- Git (for cloning)

### Installation Steps

#### 1. Environment Preparation
```bash
# Create project directory
mkdir family-budget-project
cd family-budget-project

# Clone repository
git clone https://github.com/yourusername/family-budget-app.git .

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

#### 2. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 3. Configure Environment
Create `.env` file in project root:
```
DEBUG=True
SECRET_KEY=your-very-secret-key-here-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

**For Production:**
```
DEBUG=False
SECRET_KEY=generate-a-strong-key-with-secrets-module
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:password@localhost/family_budget
```

#### 4. Database Setup
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser (admin)
python manage.py createsuperuser
# Follow prompts to create admin account
```

#### 5. Create Static Files
```bash
python manage.py collectstatic --noinput
```

#### 6. Run Development Server
```bash
python manage.py runserver
```

Server will be available at: `http://127.0.0.1:8000/`

---

## Initial Setup & Configuration

### 1. Access Admin Panel
1. Go to `http://localhost:8000/admin/`
2. Login with superuser credentials
3. Navigate to Family Budget Management section

### 2. Create Your First Family
1. Click "Families" → Add Family
2. Enter family name (e.g., "Smith Family")
3. Save (auth_code is auto-generated)
4. Note the authorization code for inviting members

### 3. Create Family Member
1. Click "Members" → Add Member
2. Select your user account
3. Select the family you just created
4. Save

### 4. Create Categories
1. From admin, click "Categories" → Add Category
2. Create default categories:
   - **Income**: Salary, Bonus, Freelance
   - **Expense**: Groceries, Utilities, Transportation
   - **Saving**: Emergency Fund, Vacation, Education

### 5. Access Dashboard
1. Logout from admin
2. Go to `http://localhost:8000/app/`
3. You should see the dashboard

---

## Project Structure Explained

```
family-budget-app/
│
├── manage.py                          # Django management script
├── requirements.txt                   # Python dependencies
├── README.md / README_ja.md           # Documentation
├── LICENSE / LICENSE_ja.md            # License files
├── .gitignore                         # Git ignore rules
│
├── family_budget_app/                 # Main Django project
│   ├── __init__.py
│   ├── settings.py                    # Project settings
│   ├── urls.py                        # URL routing
│   ├── wsgi.py                        # WSGI configuration
│   └── asgi.py                        # ASGI configuration
│
└── family_app/                        # Main application
    ├── migrations/                    # Database migrations
    ├── models.py                      # Data models
    ├── views.py                       # View logic
    ├── forms.py                       # Django forms
    ├── urls.py                        # App URLs
    ├── admin.py                       # Admin configuration
    ├── apps.py                        # App configuration
    │
    ├── templates/                     # HTML templates
    │   ├── base.html
    │   ├── dashboard.html
    │   ├── logs.html
    │   ├── budget.html
    │   ├── recurring.html
    │   ├── events.html
    │   ├── family_settings.html
    │   └── registration/
    │       └── login.html
    │
    └── static/                        # Static files
        ├── css/
        │   └── style.css
        └── js/
            └── main.js
```

---

## Common Tasks

### Add a New Family Member
**Option 1: Via Admin**
1. Create user account in Django admin
2. Create Member linking user to family

**Option 2: Via Django Shell**
```python
python manage.py shell
from django.contrib.auth.models import User
from family_app.models import Family, Member

user = User.objects.create_user('newuser', 'email@example.com', 'password')
family = Family.objects.get(name='Smith Family')
member = Member.objects.create(user=user, family=family)
```

### Create Categories Programmatically
```python
python manage.py shell
from family_app.models import Family, Category

family = Family.objects.get(name='Smith Family')

categories_data = [
    ('Salary', 'income'),
    ('Groceries', 'expense'),
    ('Emergency Fund', 'saving'),
]

for name, type_ in categories_data:
    Category.objects.create(family=family, name=name, type=type_)
```

### Reset Database
```bash
# Delete old migrations (except __init__.py)
rm family_app/migrations/0*.py

# Delete database
rm db.sqlite3

# Recreate
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

---

## Troubleshooting

### Port 8000 Already in Use
```bash
# Use different port
python manage.py runserver 8001

# Or kill process using port 8000
# macOS/Linux:
lsof -ti:8000 | xargs kill -9
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Static Files Not Loading
```bash
python manage.py collectstatic --noinput
python manage.py runserver
```

### Database Lock Error
```bash
rm db.sqlite3
python manage.py migrate
```

### Import Error / Module Not Found
```bash
# Ensure venv is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall requirements
pip install -r requirements.txt
```

### Template Not Found
1. Check template file exists in correct directory
2. Verify `TEMPLATES['DIRS']` in settings.py
3. Restart server

---

## Deployment

### Using Gunicorn

```bash
pip install gunicorn
gunicorn family_budget_app.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### Using Docker

**Dockerfile:**
```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "family_budget_app.wsgi:application", "--bind", "0.0.0.0:8000"]
```

**docker-compose.yml:**
```yaml
version: '3'
services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - SECRET_KEY=your-secret-key
  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=family_budget
      - POSTGRES_PASSWORD=password
```

### Production Checklist
- [ ] Set `DEBUG=False`
- [ ] Update `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Use HTTPS
- [ ] Set up logging
- [ ] Use PostgreSQL instead of SQLite
- [ ] Set up backups
- [ ] Configure email backend
- [ ] Enable CSRF protection
- [ ] Set secure cookies

---

## Development Tips

### Run Tests
```bash
python manage.py test family_app
```

### Create Test Data
```python
python manage.py shell
# Use Django shell to create sample data
```

### View Queries
```python
# In settings.py development:
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

### Debug Mode
```python
# In views.py
from django.shortcuts import render
from django.http import JsonResponse
import traceback

# Add to any view:
print("Debug:", variable_name)
```

---

## Getting Help

1. Check documentation files (README.md, README_ja.md)
2. Review Django documentation: https://docs.djangoproject.com/
3. Open GitHub issues for bugs
4. Check troubleshooting section above
5. Review code comments

---

## Next Steps

After successful setup:

1. **Customize Categories**: Add categories specific to your family
2. **Set Budget Limits**: Create realistic budgets for expense tracking
3. **Invite Members**: Add family members to the app
4. **Start Logging**: Begin recording transactions
5. **Schedule Recurring**: Set up recurring expenses/income
6. **Plan Events**: Add future financial events

---

Version: 1.0.0
Last Updated: 2025