# Family Budget App - Production Deployment Guide

## 🚀 Deployment Overview

This guide covers deploying the Family Budget App to production environments with best practices for security, performance, and reliability.

---

## 📋 Pre-Deployment Checklist

### Security
- [ ] Set `DEBUG = False` in settings.py
- [ ] Generate strong `SECRET_KEY`
- [ ] Update `ALLOWED_HOSTS` with your domain
- [ ] Set up HTTPS/SSL certificate
- [ ] Configure secure cookies (HTTPS only)
- [ ] Enable CSRF protection
- [ ] Set security headers
- [ ] Configure CORS if needed
- [ ] Review database credentials
- [ ] Set up environment variables securely

### Performance
- [ ] Run `collectstatic`
- [ ] Minify CSS and JavaScript
- [ ] Set up caching (Redis/Memcached)
- [ ] Configure CDN for static files
- [ ] Set up database backups
- [ ] Enable query optimization
- [ ] Configure logging
- [ ] Set up monitoring

### Operations
- [ ] Test migrations on staging
- [ ] Set up monitoring and alerts
- [ ] Plan rollback procedure
- [ ] Set up maintenance window
- [ ] Configure uptime monitoring
- [ ] Document deployment process
- [ ] Train team members
- [ ] Set up CI/CD pipeline

---

## 🌐 Deployment Options

### Option 1: PythonAnywhere (Easiest)

**Pros**: Easy setup, no server management, free tier available
**Cons**: Limited customization, pricing increases with usage

#### Steps:
1. Create account at https://www.pythonanywhere.com/
2. Upload code via Git or file upload
3. Configure virtual environment
4. Set up web app with Django
5. Configure database (PostgreSQL recommended)
6. Add static files configuration
7. Set domain name

#### Configuration:
```
Web app: /home/username/mysite/family_budget_app/wsgi.py
Python: 3.10
Virtual env: /home/username/.virtualenvs/mysite
```

---

### Option 2: Heroku (Quick & Easy)

**Pros**: Git-based deployment, free tier, great documentation
**Cons**: Monthly costs, limited free tier, vendor lock-in

#### Setup:
```bash
# Install Heroku CLI
brew tap heroku/brew && brew install heroku

# Login
heroku login

# Create app
heroku create your-app-name

# Set environment variables
heroku config:set DEBUG=False
heroku config:set SECRET_KEY=your-secret-key
heroku config:set ALLOWED_HOSTS=your-app-name.herokuapp.com

# Add Procfile to root:
web: gunicorn family_budget_app.wsgi
release: python manage.py migrate

# Deploy
git push heroku main
```

#### Procfile:
```
web: gunicorn family_budget_app.wsgi --log-file -
release: python manage.py migrate && python manage.py collectstatic --noinput
```

---

### Option 3: AWS (Scalable & Professional)

**Pros**: Scalable, powerful, widely used, free tier available
**Cons**: Complex setup, higher learning curve, potential cost

#### Using Elastic Beanstalk:

```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init -p python-3.10 family-budget

# Create environment
eb create production

# Set environment variables
eb setenv DEBUG=False SECRET_KEY=your-key ALLOWED_HOSTS=yourdomain.com

# Deploy
eb deploy
```

#### .ebextensions/django.config:
```yaml
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: family_budget_app/wsgi.py
  aws:elasticbeanstalk:application:environment:
    PYTHONPATH: /var/app/current:$PYTHONPATH
    DJANGO_SETTINGS_MODULE: family_budget_app.settings

commands:
  01_migrate:
    command: "python manage.py migrate"
    leader_only: true
  02_collectstatic:
    command: "python manage.py collectstatic --noinput"
```

---

### Option 4: DigitalOcean (Affordable & Flexible)

**Pros**: Affordable, simple interface, good documentation
**Cons**: Manual setup required, need server management

#### Droplet Setup (Ubuntu 22.04):

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3-pip python3-venv postgresql nginx -y

# Create app directory
sudo mkdir -p /var/www/family-budget
cd /var/www/family-budget

# Clone repository
sudo git clone <repo-url> .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
pip install gunicorn

# Configure database
sudo -u postgres psql
CREATE DATABASE family_budget;
CREATE USER budget_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE family_budget TO budget_user;
\q

# Set environment variables
sudo nano .env
# Add: DEBUG=False, SECRET_KEY=..., DATABASE_URL=postgresql://...

# Collect static files
python manage.py collectstatic --noinput

# Create systemd service
sudo nano /etc/systemd/system/gunicorn.service
```

#### gunicorn.service:
```ini
[Unit]
Description=gunicorn daemon for family budget
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/family-budget
ExecStart=/var/www/family-budget/venv/bin/gunicorn \
          --workers 3 \
          --bind unix:/run/gunicorn.sock \
          family_budget_app.wsgi

[Install]
WantedBy=multi-user.target
```

#### Nginx Configuration:
```bash
sudo nano /etc/nginx/sites-available/family-budget
```

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias /var/www/family-budget/staticfiles/;
    }

    location /media/ {
        alias /var/www/family-budget/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
}
```

```bash
# Enable site and restart
sudo ln -s /etc/nginx/sites-available/family-budget /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
```

---

### Option 5: Docker (Container-Based)

**Pros**: Consistent environment, easy to scale, portable
**Cons**: Requires Docker knowledge, additional orchestration needed

#### Docker Deployment:

```bash
# Build image
docker build -t family-budget:latest .

# Run container
docker run -d \
  --name family-budget \
  -e DEBUG=False \
  -e SECRET_KEY=your-secret \
  -p 8000:8000 \
  family-budget:latest

# With Docker Compose
docker-compose up -d

# Push to Docker Hub
docker tag family-budget:latest username/family-budget:latest
docker push username/family-budget:latest
```

#### Production Docker Compose:

```yaml
version: '3.8'
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: family_budget
      POSTGRES_USER: budget_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always

  web:
    build: .
    command: >
      sh -c "python manage.py migrate &&
             python manage.py collectstatic --noinput &&
             gunicorn family_budget_app.wsgi:application --bind 0.0.0.0:8000 --workers 4"
    environment:
      DEBUG: "False"
      SECRET_KEY: ${SECRET_KEY}
      ALLOWED_HOSTS: ${ALLOWED_HOSTS}
      DATABASE_URL: postgresql://budget_user:${DB_PASSWORD}@db:5432/family_budget
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    depends_on:
      - db
    restart: always

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - static_volume:/app/staticfiles
      - media_volume:/app/media
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web
    restart: always

volumes:
  postgres_data:
  static_volume:
  media_volume:
```

---

## 🔐 Security Configuration

### Django Settings for Production

```python
# settings.py

DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
SECRET_KEY = os.environ.get('SECRET_KEY')

# HTTPS Settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Security Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = {
    'default-src': ("'self'",),
    'script-src': ("'self'", "cdn.jsdelivr.net"),
    'style-src': ("'self'", "cdn.jsdelivr.net"),
    'img-src': ("'self'", "data:"),
}

# Database (PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'family_budget'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL')

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/error.log',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### SSL Certificate Setup

#### Let's Encrypt with Certbot (Free):

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot certonly --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

# Test renewal
sudo certbot renew --dry-run
```

---

## 🗄️ Database Management

### PostgreSQL Setup

```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Create database and user
sudo -u postgres psql
CREATE DATABASE family_budget;
CREATE USER budget_user WITH PASSWORD 'strong_password_here';
ALTER ROLE budget_user SET client_encoding TO 'utf8';
ALTER ROLE budget_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE budget_user SET default_transaction_deferrable TO on;
GRANT ALL PRIVILEGES ON DATABASE family_budget TO budget_user;
\q

# Backup database
pg_dump family_budget > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore database
psql family_budget < backup_file.sql
```

### Automated Backups

```bash
# Create backup script: /usr/local/bin/backup-db.sh
#!/bin/bash
BACKUP_DIR="/var/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump family_budget | gzip > $BACKUP_DIR/family_budget_$DATE.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -mtime +30 -delete

# Add to crontab
sudo crontab -e
# Add: 0 2 * * * /usr/local/bin/backup-db.sh
```

---

## 📊 Monitoring & Logging

### Application Monitoring

```python
# Add to settings.py for monitoring
SENTRY_DSN = os.environ.get('SENTRY_DSN')

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        traces_sample_rate=0.1,
        send_default_pii=False
    )
```

### System Monitoring Script

```bash
#!/bin/bash
# monitor.sh - Monitor server health

log_file="/var/log/family-budget-monitor.log"

# Check disk space
disk_usage=$(df / | tail -1 | awk '{print $5}' | cut -d% -f1)
if [ $disk_usage -gt 80 ]; then
    echo "$(date): ALERT - Disk usage at ${disk_usage}%" >> $log_file
fi

# Check memory
memory_usage=$(free | grep Mem | awk '{print int($3/$2 * 100)}')
if [ $memory_usage -gt 80 ]; then
    echo "$(date): ALERT - Memory usage at ${memory_usage}%" >> $log_file
fi

# Check service
if ! systemctl is-active --quiet gunicorn; then
    echo "$(date): ALERT - Gunicorn service is down" >> $log_file
    systemctl restart gunicorn
fi

# Check database connection
python3 -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'family_budget_app.settings')
django.setup()
from django.db import connection
connection.ensure_connection()
" 2>/dev/null || echo "$(date): ALERT - Database connection failed" >> $log_file
```

---

## 🔄 Continuous Integration/Deployment

### GitHub Actions CI/CD

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run migrations
        run: python manage.py migrate

      - name: Run tests
        run: python manage.py test

      - name: Collect static files
        run: python manage.py collectstatic --noinput

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v2

      - name: Deploy to DigitalOcean
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /var/www/family-budget
            git pull origin main
            source venv/bin/activate
            pip install -r requirements.txt
            python manage.py migrate
            python manage.py collectstatic --noinput
            sudo systemctl restart gunicorn
```

---

## 🚨 Maintenance & Updates

### Regular Maintenance Schedule

```
Weekly:
- Review error logs
- Check disk space
- Monitor database size
- Verify backups

Monthly:
- Update dependencies
- Review security patches
- Performance analysis
- Clean up old logs

Quarterly:
- Full security audit
- Database optimization
- Capacity planning
- User feedback review

Annually:
- Full system review
- Architecture assessment
- Compliance audit
- Disaster recovery drill
```

### Django/Package Updates

```bash
# Check for updates
pip list --outdated

# Update packages safely
pip install --upgrade Django==4.2.8
python manage.py test  # Test after update
python manage.py runserver  # Manual testing

# Update all packages
pip install -r requirements.txt --upgrade
```

### Database Maintenance

```bash
# Analyze table performance
ANALYZE;

# Vacuum database (PostgreSQL)
VACUUM ANALYZE;

# Index maintenance
REINDEX INDEX index_name;

# View slow queries
SELECT query, calls, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

---

## 🔄 Rollback Procedures

### Git-based Rollback

```bash
# View commit history
git log --oneline

# Rollback to previous version
git revert <commit-hash>
git push origin main

# Or reset to specific commit
git reset --hard <commit-hash>
git push origin main --force
```

### Database Rollback

```bash
# List backups
ls -lh /var/backups/postgres/

# Stop application
sudo systemctl stop gunicorn

# Restore from backup
gunzip < /var/backups/postgres/family_budget_20240115_020000.sql.gz | psql family_budget

# Restart application
sudo systemctl start gunicorn
```

---

## 📈 Performance Optimization

### Database Query Optimization

```python
# Use select_related for ForeignKey
logs = Log.objects.select_related('family', 'member', 'category')

# Use prefetch_related for reverse relations
families = Family.objects.prefetch_related('categories', 'logs')

# Use only and defer to reduce fields
users = User.objects.only('username', 'email')

# Add database indexes
class Log(models.Model):
    date = models.DateField(db_index=True)
    family = models.ForeignKey(Family, db_index=True)
```

### Caching Strategy

```python
# In views.py
from django.views.decorators.cache import cache_page
from django.core.cache import cache

@cache_page(60 * 5)  # Cache for 5 minutes
def dashboard(request):
    # View logic
    pass

# Or manual caching
cache_key = f'family_{family_id}_dashboard'
data = cache.get(cache_key)
if not data:
    data = calculate_dashboard_data(family_id)
    cache.set(cache_key, data, 300)  # Cache for 5 minutes
```

### Static File Optimization

```bash
# Minify CSS
python -m pip install django-compressor
# Configure in settings and templates

# Use CDN for static files
# Configure CloudFront, Cloudflare, or similar
```

---

## ✅ Deployment Checklist

### Pre-Deployment
- [ ] All tests passing
- [ ] Code reviewed
- [ ] Database migrations tested
- [ ] Static files collected
- [ ] Environment variables set
- [ ] Backups verified
- [ ] Monitoring configured

### Deployment
- [ ] Deploy code
- [ ] Run migrations
- [ ] Restart services
- [ ] Verify application loads
- [ ] Check all pages
- [ ] Test login/authentication
- [ ] Verify static files load

### Post-Deployment
- [ ] Monitor error logs
- [ ] Check application performance
- [ ] Verify email sending
- [ ] Test scheduled tasks
- [ ] Document changes
- [ ] Notify team
- [ ] Plan rollback if needed

---

## 🆘 Emergency Procedures

### Application Down

```bash
# Check service status
sudo systemctl status gunicorn
sudo systemctl status nginx

# View recent logs
sudo tail -f /var/log/syslog
sudo tail -f /var/log/nginx/error.log

# Restart services
sudo systemctl restart gunicorn
sudo systemctl restart nginx

# If database is down
sudo systemctl restart postgresql
```

### Database Corruption

```bash
# Stop application
sudo systemctl stop gunicorn

# Check database
sudo -u postgres pg_dump family_budget > /tmp/dump.sql

# Restore from backup
sudo -u postgres psql family_budget < /var/backups/backup.sql

# Verify
sudo -u postgres psql family_budget -c "SELECT COUNT(*) FROM family_app_family;"

# Restart application
sudo systemctl start gunicorn
```

### Disk Full

```bash
# Find large files
sudo du -sh /* | sort -rh

# Clean old logs
sudo journalctl --vacuum=time=7d

# Clean package cache
sudo apt clean
sudo apt autoclean

# Clean old database backups
find /var/backups/postgres -mtime +30 -delete
```

---

## 📞 Support & Resources

### Production Support Contacts
- **Django Docs**: https://docs.djangoproject.com/
- **PostgreSQL Docs**: https://www.postgresql.org/docs/
- **Nginx Docs**: https://nginx.org/en/docs/
- **Ubuntu Docs**: https://ubuntu.com/server/docs

### Useful Commands

```bash
# Django shell for debugging
python manage.py shell

# Create backup
python manage.py dumpdata > backup.json

# Load backup
python manage.py loaddata backup.json

# Check for security issues
python manage.py check --deploy

# View environment
python manage.py diffsettings
```

---

**Version**: 1.0.0  
**Last Updated**: 2025 
**Deployment Status**: Ready for Production