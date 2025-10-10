# ============================================================================
# manage_data.py - Utility script for common data management tasks
# ============================================================================
"""
Place this file in the root directory and run:
python manage_data.py create_sample_data
python manage_data.py reset_family <family_name>
python manage_data.py generate_report <family_name>
"""

import os
import sys
import django
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'family_budget_app.settings')
django.setup()

from django.contrib.auth.models import User
from family_app.models import Family, Member, Category, Log, BudgetLimit, RecurringLog, FutureEvent

def create_sample_family():
    """Create sample family with demo data"""
    print("Creating sample family data...")
    
    # Create or get family
    family, created = Family.objects.get_or_create(name='Demo Family')
    
    # Create sample user
    user, _ = User.objects.get_or_create(
        username='demo_user',
        defaults={'email': 'demo@example.com', 'first_name': 'Demo', 'last_name': 'User'}
    )
    if _ :
        user.set_password('demo123')
        user.save()
    
    # Create member
    member, _ = Member.objects.get_or_create(user=user, family=family)
    
    # Create categories
    categories_data = [
        ('Salary', 'income'),
        ('Bonus', 'income'),
        ('Groceries', 'expense'),
        ('Utilities', 'expense'),
        ('Transportation', 'expense'),
        ('Entertainment', 'expense'),
        ('Emergency Fund', 'saving'),
        ('Vacation Fund', 'saving'),
    ]
    
    categories = {}
    for name, type_ in categories_data:
        cat, _ = Category.objects.get_or_create(
            family=family, name=name,
            defaults={'type': type_}
        )
        categories[name] = cat
    
    # Create sample logs (last 30 days)
    today = timezone.now().date()
    logs_data = [
        (categories['Salary'], Decimal('3000'), 'Monthly salary', 'income'),
        (categories['Groceries'], Decimal('150'), 'Weekly groceries', 'expense'),
        (categories['Utilities'], Decimal('120'), 'Electricity and water', 'expense'),
        (categories['Transportation'], Decimal('50'), 'Gas', 'expense'),
        (categories['Emergency Fund'], Decimal('500'), 'Monthly savings', 'saving'),
    ]
    
    for category, amount, description, _ in logs_data:
        for i in range(0, 30, 7):
            log_date = today - timedelta(days=i)
            Log.objects.get_or_create(
                family=family,
                member=member,
                category=category,
                amount=amount,
                date=log_date,
                defaults={'description': description}
            )
    
    # Create budget limits
    budget_data = [
        (categories['Groceries'], Decimal('600')),
        (categories['Utilities'], Decimal('200')),
        (categories['Entertainment'], Decimal('300')),
    ]
    
    for category, limit in budget_data:
        BudgetLimit.objects.get_or_create(
            family=family,
            category=category,
            defaults={'amount_limit': limit, 'period': 'monthly'}
        )
    
    # Create recurring logs
    RecurringLog.objects.get_or_create(
        family=family,
        category=categories['Salary'],
        amount=Decimal('3000'),
        defaults={
            'recurrence': 'monthly',
            'start_date': today,
            'active': True,
            'description': 'Monthly salary'
        }
    )
    
    # Create future events
    FutureEvent.objects.get_or_create(
        family=family,
        name='Vacation',
        amount=Decimal('2000'),
        event_date=today + timedelta(days=60),
        defaults={'type': 'expense', 'description': 'Summer vacation'}
    )
    
    print("✓ Sample data created successfully!")
    print(f"  Family: {family.name}")
    print(f"  Username: demo_user")
    print(f"  Password: demo123")

def reset_family(family_name):
    """Reset all data for a family"""
    try:
        family = Family.objects.get(name=family_name)
        
        # Delete all related data
        Log.objects.filter(family=family).delete()
        BudgetLimit.objects.filter(family=family).delete()
        RecurringLog.objects.filter(family=family).delete()
        FutureEvent.objects.filter(family=family).delete()
        Category.objects.filter(family=family).delete()
        Member.objects.filter(family=family).delete()
        family.delete()
        
        print(f"✓ Family '{family_name}' reset successfully!")
    except Family.DoesNotExist:
        print(f"✗ Family '{family_name}' not found!")

def generate_report(family_name):
    """Generate financial report for a family"""
    try:
        family = Family.objects.get(name=family_name)
        
        print(f"\n{'='*50}")
        print(f"Financial Report: {family.name}")
        print(f"{'='*50}")
        
        # Summary
        today = timezone.now().date()
        month_start = today.replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        logs = Log.objects.filter(family=family, date__range=[month_start, month_end])
        
        income = logs.filter(category__type='income').aggregate(
            Sum=django.db.models.Sum('amount')
        )['Sum'] or Decimal('0')
        
        expense = logs.filter(category__type='expense').aggregate(
            Sum=django.db.models.Sum('amount')
        )['Sum'] or Decimal('0')
        
        saving = logs.filter(category__type='saving').aggregate(
            Sum=django.db.models.Sum('amount')
        )['Sum'] or Decimal('0')
        
        balance = income - expense - saving
        
        print(f"\nMonth: {month_start.strftime('%B %Y')}")
        print(f"  Income:  ${income:>10.2f}")
        print(f"  Expense: ${expense:>10.2f}")
        print(f"  Saving:  ${saving:>10.2f}")
        print(f"  Balance: ${balance:>10.2f}")
        
        # Budget status
        print(f"\n{'Budgets':^50}")
        print("-" * 50)
        budgets = BudgetLimit.objects.filter(family=family)
        for budget in budgets:
            spent = logs.filter(category=budget.category).aggregate(
                Sum=django.db.models.Sum('amount')
            )['Sum'] or Decimal('0')
            
            percentage = (spent / budget.amount_limit * 100) if budget.amount_limit else 0
            status = "✓" if percentage <= 100 else "✗"
            
            print(f"{status} {budget.category.name:20} ${spent:>8.2f} / ${budget.amount_limit:>8.2f} ({percentage:>6.1f}%)")
        
        # Upcoming events
        upcoming = FutureEvent.objects.filter(
            family=family,
            event_date__gte=today
        ).order_by('event_date')[:5]
        
        if upcoming:
            print(f"\n{'Upcoming Events':^50}")
            print("-" * 50)
            for event in upcoming:
                print(f"  {event.name:30} ${event.amount:>8.2f} on {event.event_date}")
        
        print(f"\n{'='*50}\n")
        
    except Family.DoesNotExist:
        print(f"✗ Family '{family_name}' not found!")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python manage_data.py create_sample_data")
        print("  python manage_data.py reset_family <family_name>")
        print("  python manage_data.py generate_report <family_name>")
    elif sys.argv[1] == 'create_sample_data':
        create_sample_family()
    elif sys.argv[1] == 'reset_family' and len(sys.argv) > 2:
        reset_family(sys.argv[2])
    elif sys.argv[1] == 'generate_report' and len(sys.argv) > 2:
        generate_report(sys.argv[2])
    else:
        print("✗ Invalid arguments!")