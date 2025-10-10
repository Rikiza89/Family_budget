# Family Budget App - Command Reference & Cheat Sheet

## 🚀 Quickest Start Commands

```bash
# Total: ~2 minutes to get running

# 1. Clone and navigate
git clone https://github.com/yourusername/family-budget-app.git
cd family-budget-app

# 2. Setup environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Initialize database
python manage.py migrate

# 4. Create admin account
python manage.py createsuperuser

# 5. Run server
python manage.py runserver

# 6. Visit http://localhost:8000
```

---

## 📦 Dependency Management

### Install Dependencies
```bash
# Install from requirements.txt
pip install -r requirements.txt

# Install specific package
pip install Django==4.2.7

# Install with specific version
pip install "Django>=4.2,<5.0"

# Upgrade specific package
pip install --upgrade Django

# Upgrade all packages
pip install -r requirements.txt --upgrade

# Show installed packages
pip list

# Show outdated packages
pip list --outdated

# Create requirements from installed
pip freeze > requirements.txt

# Install development dependencies
pip install pytest pytest-django coverage
```

---

## 🗄️ Database Commands

### Migrations
```bash
# Create migrations for changes
python manage.py makemigrations

# Create migrations for specific app
python manage.py makemigrations family_app

# Show migration status
python manage.py showmigrations

# Run migrations
python manage.py migrate

# Run specific migration
python manage.py migrate family_app 0001

# Reverse migration
python manage.py migrate family_app 0001

# Squash migrations
python manage.py squashmigrations family_app 0001 0010

# List databases
python manage.py dbshell  # Access database shell
```

### Database Backup & Restore
```bash
# Dump data to JSON
python manage.py dumpdata > backup.json

# Dump specific model
python manage.py dumpdata family_app.Log > logs_backup.json

# Dump pretty formatted
python manage.py dumpdata --indent=4 > backup.json

# Load data from JSON
python manage.py loaddata backup.json

# Load specific file
python manage.py loaddata logs_backup.json

# PostgreSQL backup
pg_dump family_budget > backup.sql

# PostgreSQL restore
psql family_budget < backup.sql

# PostgreSQL compressed backup
pg_dump family_budget | gzip > backup.sql.gz

# PostgreSQL restore from compressed
gunzip < backup.sql.gz | psql family_budget
```

### Database Inspection
```bash
# Access database shell
python manage.py dbshell

# SQL inspect queries
python manage.py sqlmigrate family_app 0001

# Check database
python manage.py check

# Database statistics
python manage.py dbshell
SELECT COUNT(*) FROM family_app_family;
SELECT COUNT(*) FROM family_app_log;
SELECT COUNT(*) FROM family_app_member;
```

---

## 👤 User & Auth Commands

### Create Users
```bash
# Create superuser (interactive)
python manage.py createsuperuser

# Create superuser (non-interactive)
python manage.py createsuperuser \
  --username admin \
  --email admin@example.com \
  --noinput

# Create regular user (shell)
python manage.py shell
from django.contrib.auth.models import User
User.objects.create_user('username', 'email@example.com', 'password')
```

### Reset Password
```bash
# Reset in shell
python manage.py shell
from django.contrib.auth.models import User
user = User.objects.get(username='username')
user.set_password('newpassword')
user.save()

# Or use command
python manage.py changepassword username
```

### Manage Permissions
```bash
# In Django shell
from django.contrib.auth.models import User, Permission
user = User.objects.get(username='username')
permission = Permission.objects.get(codename='add_family')
user.user_permissions.add(permission)
```

---

## 🧪 Testing Commands

### Run Tests
```bash
# Run all tests
python manage.py test

# Run app tests
python manage.py test family_app

# Run specific test file
python manage.py test family_app.tests

# Run specific test class
python manage.py test family_app.tests.FamilyModelTest

# Run specific test method
python manage.py test family_app.tests.FamilyModelTest.test_family_creation

# Run with verbosity
python manage.py test --verbosity=2

# Run and keep database
python manage.py test --keepdb

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Testing Utilities
```bash
# Check test coverage
coverage run --source='.' manage.py test family_app
coverage report -m
coverage html  # Generate HTML report

# Run specific test pattern
python manage.py test -k "test_dashboard"

# Fail fast
python manage.py test --failfast

# Parallel testing
python manage.py test --parallel 4
```

---

## 🛠️ Development Commands

### Django Shell
```bash
# Open interactive Python shell with Django
python manage.py shell

# Then in shell:
from family_app.models import Family, Member, Log
family = Family.objects.first()
print(family)
members = family.members.all()
print(members.count())
```

### Create Django App
```bash
# Create new app
python manage.py startapp app_name

# Create app with custom template
python manage.py startapp app_name --template=path/to/template
```

### Management Commands
```bash
# List all commands
python manage.py help

# Get help for specific command
python manage.py help runserver

# Show all available commands
python manage.py help --all
```

### Static Files
```bash
# Collect static files
python manage.py collectstatic

# Collect without confirmation
python manage.py collectstatic --noinput

# Collect and clear old
python manage.py collectstatic --clear --noinput

# Find static files
python manage.py findstatic style.css

# List all static files
python manage.py collectstatic --dry-run --noinput
```

### Check & Debug
```bash
# Check project configuration
python manage.py check

# Check deployment settings
python manage.py check --deploy

# Show Django settings
python manage.py diffsettings

# Generate SQL
python manage.py sqlmigrate family_app 0001

# Show installed apps
python manage.py showmigrations
```

---

## 🚀 Server & Deployment Commands

### Development Server
```bash
# Run on default port (8000)
python manage.py runserver

# Run on specific port
python manage.py runserver 8001

# Run on all interfaces
python manage.py runserver 0.0.0.0:8000

# Run with reload disabled
python manage.py runserver --noreload

# Run with debugging enabled
python manage.py runserver --debug-mode
```

### Production Server (Gunicorn)
```bash
# Install gunicorn
pip install gunicorn

# Run with default settings
gunicorn family_budget_app.wsgi:application

# Run on specific port
gunicorn family_budget_app.wsgi:application --bind 0.0.0.0:8000

# Run with multiple workers
gunicorn family_budget_app.wsgi:application --workers 4

# Run with specific worker class
gunicorn family_budget_app.wsgi:application \
  --worker-class sync \
  --workers 4 \
  --bind 0.0.0.0:8000

# Run with logging
gunicorn family_budget_app.wsgi:application \
  --access-logfile - \
  --error-logfile - \
  --log-level debug

# Run as daemon
gunicorn family_budget_app.wsgi:application \
  --daemon \
  --bind 0.0.0.0:8000 \
  --pid /var/run/gunicorn.pid
```

### Production Server (uWSGI)
```bash
# Install uWSGI
pip install uwsgi

# Run uWSGI
uwsgi --http :8000 --wsgi-file family_budget_app/wsgi.py --master --processes 4

# With configuration file
uwsgi --ini config.ini
```

---

## 🐳 Docker Commands

### Docker Basics
```bash
# Build image
docker build -t family-budget:latest .

# Run container
docker run -d -p 8000:8000 family-budget:latest

# Run with environment variables
docker run -d \
  -p 8000:8000 \
  -e DEBUG=False \
  -e SECRET_KEY=your-secret \
  family-budget:latest

# View logs
docker logs container-id

# Stop container
docker stop container-id

# Remove container
docker rm container-id

# Execute command in container
docker exec -it container-id bash

# Access container shell
docker exec -it container-id python manage.py shell
```

### Docker Compose
```bash
# Start services
docker-compose up

# Start in background
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs

# View specific service logs
docker-compose logs web

# Execute command
docker-compose exec web python manage.py migrate

# Rebuild images
docker-compose build

# Scale service
docker-compose up -d --scale web=3

# Remove volumes
docker-compose down -v
```

---

## 🔧 Git Commands

### Basic Git Workflow
```bash
# Clone repository
git clone https://github.com/yourusername/family-budget-app.git

# Create branch
git checkout -b feature/new-feature

# Check status
git status

# Add changes
git add .

# Commit changes
git commit -m "Add new feature"

# Push to remote
git push origin feature/new-feature

# Create pull request (on GitHub)

# Merge after approval
git checkout main
git merge feature/new-feature

# Delete branch
git branch -d feature/new-feature
git push origin --delete feature/new-feature
```

### Git Maintenance
```bash
# View commit history
git log --oneline

# View specific commits
git log --author="Name"

# Revert to previous commit
git revert commit-hash

# Hard reset (careful!)
git reset --hard commit-hash

# Push to remote
git push origin main

# Force push (use with caution)
git push origin main --force

# Pull latest changes
git pull origin main

# Stash changes
git stash

# Apply stashed changes
git stash pop
```

---

## 📊 Utility Scripts Commands

### Sample Data
```bash
# Create sample family data
python manage_data.py create_sample_data

# Expected output:
# ✓ Sample data created successfully!
#   Family: Demo Family
#   Username: demo_user
#   Password: demo123
```

### Reports
```bash
# Generate financial report
python manage_data.py generate_report "Demo Family"

# Expected output:
# ==================================================
# Financial Report: Demo Family
# ==================================================
# Month: January 2024
#   Income:      $3000.00
#   Expense:     $220.00
#   Saving:      $500.00
#   Balance:     $2280.00
# Budgets
# --------------------------------------------------
# ...
```

### Reset Data
```bash
# Reset family and all related data
python manage_data.py reset_family "Demo Family"

# Expected output:
# ✓ Family 'Demo Family' reset successfully!
```

---

## 📝 System Commands

### Linux/macOS
```bash
# Activate virtual environment
source venv/bin/activate

# Deactivate virtual environment
deactivate

# Check Python version
python --version

# Check pip version
pip --version

# List Python packages
pip list

# View file
cat manage.py

# Copy file
cp file.py backup_file.py

# Remove file
rm file.py

# Create directory
mkdir new_directory

# Navigate directory
cd directory_name

# Current directory
pwd

# List files
ls -la

# Find files
find . -name "*.py"

# Count lines of code
wc -l family_app/views.py

# Search in files
grep -r "keyword" family_app/

# Check system resources
top
```

### Windows (PowerShell/CMD)
```bash
# Activate virtual environment
venv\Scripts\activate

# Deactivate virtual environment
deactivate

# Check Python version
python --version

# Check pip version
pip --version

# List Python packages
pip list

# View file
type manage.py

# Copy file
copy file.py backup_file.py

# Remove file
del file.py

# Create directory
mkdir new_directory

# Navigate directory
cd directory_name

# Current directory
cd

# List files
dir

# Find files
where /R . *.py

# Count lines
find . -name "*.py" | measure-object -line
```

---

## 🌐 Web Server Commands

### Nginx
```bash
# Test configuration
nginx -t

# Start Nginx
sudo systemctl start nginx

# Stop Nginx
sudo systemctl stop nginx

# Restart Nginx
sudo systemctl restart nginx

# Check status
sudo systemctl status nginx

# Enable on boot
sudo systemctl enable nginx

# View logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# Reload configuration
sudo nginx -s reload
```

### Systemd Services
```bash
# Start service
sudo systemctl start gunicorn

# Stop service
sudo systemctl stop gunicorn

# Restart service
sudo systemctl restart gunicorn

# Enable on boot
sudo systemctl enable gunicorn

# Check status
sudo systemctl status gunicorn

# View logs
sudo journalctl -u gunicorn -n 50

# Follow logs
sudo journalctl -u gunicorn -f
```

---

## 💾 Database Management Commands

### PostgreSQL
```bash
# Connect to database
psql -U username -d family_budget

# List databases
\l

# Connect to database
\c family_budget

# List tables
\dt

# Show table structure
\d family_app_family

# Run SQL query
SELECT COUNT(*) FROM family_app_log;

# Exit psql
\q

# Backup
pg_dump family_budget > backup.sql

# Restore
psql family_budget < backup.sql

# Create user
createuser budget_user

# Create database
createdb family_budget
```

### SQLite
```bash
# Access SQLite
sqlite3 db.sqlite3

# List tables
.tables

# Show schema
.schema family_app_log

# Run query
SELECT COUNT(*) FROM family_app_log;

# Exit
.exit

# Backup
cp db.sqlite3 db.sqlite3.backup

# Restore
cp db.sqlite3.backup db.sqlite3
```

---

## 🔍 Debugging & Logging Commands

### Django Debugging
```bash
# Debug specific view
python manage.py shell
from django.test import Client
client = Client()
response = client.get('/app/')
print(response.status_code)
print(response.context)

# Print queries
from django.db import connection, reset_queries
from django.conf import settings
settings.DEBUG = True
reset_queries()
# ... run code ...
print(connection.queries)

# Check settings
python manage.py diffsettings
```

### Log Viewing
```bash
# View all logs
tail -f /var/log/django/error.log

# View last N lines
tail -n 50 /var/log/django/error.log

# Search logs
grep "error" /var/log/django/error.log

# Follow logs in real-time
tail -f /var/log/nginx/access.log

# Count occurrences
grep -c "error" /var/log/django/error.log
```

---

## 🚨 Troubleshooting Commands

### Common Issues
```bash
# Port already in use
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process using port
kill -9 process_id  # macOS/Linux
taskkill /PID process_id /F  # Windows

# Check disk space
df -h

# Check memory usage
free -h  # Linux
vm_stat  # macOS

# Check Python path
which python
which python3

# Verify Django installation
python -c "import django; print(django.VERSION)"

# Test database connection
python manage.py dbshell

# Check static files
python manage.py findstatic style.css

# Verify installed packages
pip show Django

# Check for security issues
python manage.py check --deploy
```

---

## 📊 Performance Commands

### Django Performance
```bash
# Run Django Debug Toolbar (if installed)
pip install django-debug-toolbar

# Monitor database queries
from django.db import connection, reset_queries
settings.DEBUG = True
# ... run code ...
print(len(connection.queries))

# Profile code
python -m cProfile manage.py runserver

# Use Django extensions
pip install django-extensions
python manage.py runserver_plus
```

### System Performance
```bash
# Top processes (Linux)
top

# Memory usage
free -h

# Disk usage
du -sh *

# CPU usage
uptime

# Network connections
netstat -an

# Process list
ps aux

# Monitor real-time
watch -n 1 'free -h'
```

---

## 📚 Help & Information

### Django Help
```bash
# General help
python manage.py help

# Command help
python manage.py help migrate

# List all commands
python manage.py help --all
```

### Documentation
```bash
# View readme
cat README.md

# View setup guide
cat SETUP_GUIDE.md

# View deployment guide
cat DEPLOYMENT_GUIDE.md

# View this cheat sheet
cat COMMAND_REFERENCE.md
```

---

## ✅ Daily Development Workflow

```bash
# 1. Start day
git pull origin main
source venv/bin/activate
pip install -r requirements.txt

# 2. Create feature branch
git checkout -b feature/your-feature

# 3. Make changes
# ... edit code ...

# 4. Test changes
python manage.py test

# 5. Check formatting
python -m black .

# 6. Commit changes
git add .
git commit -m "Add feature"

# 7. Push to remote
git push origin feature/your-feature

# 8. Create pull request on GitHub

# 9. After approval, merge
git checkout main
git merge feature/your-feature
```

---

## 🎯 Quick Tips

- **Speed up pip**: `pip install -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt`
- **Virtual env cleanup**: `rm -rf venv/` then recreate
- **Forced refresh**: `python manage.py collectstatic --clear --noinput`
- **Hard reset DB**: `rm db.sqlite3 && python manage.py migrate`
- **Quick test**: `python manage.py test --failfast`
- **View all URLs**: `python manage.py show_urls`
- **Monitor tail**: `tail -f /var/log/django/error.log`

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**Status**: Complete Reference