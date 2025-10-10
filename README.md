# README.md

# Family Budget App

A comprehensive Django web application for managing family budgets, tracking expenses, and planning for future events. The app is fully responsive and optimized for both desktop and mobile devices.

## Features

- **Dashboard**: Real-time overview of income, expenses, savings, and balance
- **Transaction Logging**: Record income, expenses, and savings with descriptions
- **Budget Management**: Set and monitor spending limits for each category
- **Recurring Transactions**: Automate regular expenses and income entries
- **Future Events**: Plan and track upcoming financial events
- **Family Management**: Multiple family members can access shared family data
- **Category Management**: Create custom income, expense, and saving categories
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Multi-language Support**: English and Japanese interfaces

## Technology Stack

- **Backend**: Django 4.2.7
- **Frontend**: Bootstrap 5.3, HTML5, CSS3, JavaScript
- **Database**: SQLite (default, can be changed to PostgreSQL/MySQL)
- **Authentication**: Django built-in authentication system

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Virtual environment (recommended)

### Setup Steps

1. **Clone the repository**
```bash
git clone https://github.com/Rikiza89/family-budget-app.git
cd family-budget-app
```

2. **Create and activate virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Create superuser (admin account)**
```bash
python manage.py createsuperuser
```

6. **Run development server**
```bash
python manage.py runserver
```

7. **Access the application**
Open your browser and go to `http://127.0.0.1:8000/`

## Usage

### Creating a Family

1. Log in with your superuser account
2. Go to Django Admin (`http://127.0.0.1:8000/admin/`)
3. Create a new Family
4. Create a Member linking your user to the family
5. Access the dashboard at `http://127.0.0.1:8000/app/`

### Dashboard

View your financial overview at a glance:
- Current month's income, expenses, and savings
- Budget status and alerts
- Upcoming events within the next 30 days
- Category breakdown

### Recording Transactions

1. Navigate to **Logs** section
2. Fill in the transaction details (category, amount, date, description)
3. Click "Add Log"
4. Use date range filters to view specific transactions

### Managing Budget

1. Go to **Budget** section
2. Set spending limits for specific categories
3. Monitor your spending against limits
4. View alerts when approaching or exceeding limits

### Recurring Transactions

1. Navigate to **Recurring** section
2. Create recurring transactions (daily, weekly, monthly, etc.)
3. Set start and end dates
4. Enable/disable as needed

### Future Events

1. Go to **Events** section
2. Add upcoming financial events (income or expenses)
3. Plan ahead for major expenses or income

### Family Settings

1. Access **Settings** to manage:
   - Family information and authorization code
   - Family members
   - Custom categories

## Project Structure

```
family-budget-app/
├── manage.py
├── requirements.txt
├── README.md
├── LICENSE
├── family_budget_app/
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── family_app/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── logs.html
│   │   ├── budget.html
│   │   ├── recurring.html
│   │   ├── events.html
│   │   └── family_settings.html
│   └── static/
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── main.js
└── db.sqlite3
```

## Configuration

### Environment Variables

Create a `.env` file in the root directory:

```
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

### Database Configuration

Default: SQLite

For PostgreSQL, update `settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'family_budget',
        'USER': 'username',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## API Overview

### Models

- **Family**: Represents a distinct family unit
- **Member**: Links users to families
- **Category**: Custom transaction categories
- **Log**: Individual transactions
- **RecurringLog**: Automated recurring transactions
- **BudgetLimit**: Spending limits per category
- **FutureEvent**: Planned future transactions

### Views

- `dashboard`: Main dashboard overview
- `logs_view`: Transaction management
- `budget_view`: Budget management
- `recurring_view`: Recurring transactions
- `events_view`: Future events
- `family_settings`: Family configuration

## Mobile Optimization

The application is fully responsive with:
- Mobile-first design approach
- Touch-friendly buttons and inputs
- Optimized navigation for small screens
- Responsive tables and charts
- Fast loading times

## Language Support

The app supports both English and Japanese interfaces. Templates are provided for both languages:
- English templates: `template.html`
- Japanese templates: `template_ja.html`

## Deployment

### Production Checklist

1. Set `DEBUG=False` in settings.py
2. Update `ALLOWED_HOSTS`
3. Use a production database (PostgreSQL recommended)
4. Set a strong `SECRET_KEY`
5. Use HTTPS
6. Set up proper logging
7. Use a production server (Gunicorn, uWSGI)

### Deployment with Gunicorn

```bash
pip install gunicorn
gunicorn family_budget_app.wsgi:application --bind 0.0.0.0:8000
```

### Deployment with Docker

Create a `Dockerfile`:
```dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "family_budget_app.wsgi:application", "--bind", "0.0.0.0:8000"]
```

## Troubleshooting

### Static Files Not Loading

```bash
python manage.py collectstatic
```

### Database Errors

```bash
python manage.py makemigrations
python manage.py migrate
```

### Port Already in Use

```bash
python manage.py runserver 8001
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues, questions, or suggestions:
- Open an GitHub issue
- Check existing documentation
- Review troubleshooting section

## Acknowledgments

- Django framework
- Bootstrap CSS framework
- Bootstrap Icons
- Contributors and users

---

**Version**: 1.0.0  
**Last Updated**: 10/10/2025  
**Python Version**: 3.8+


---
