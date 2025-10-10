# ============================================================================
# tests.py - Unit tests for the application
# ============================================================================
"""
Place in: family_app/tests.py
Run: python manage.py test family_app
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
from datetime import date
from .models import Family, Member, Category, Log, BudgetLimit, FutureEvent

class FamilyModelTest(TestCase):
    def setUp(self):
        self.family = Family.objects.create(name="Test Family")
    
    def test_family_creation(self):
        self.assertEqual(self.family.name, "Test Family")
        self.assertIsNotNone(self.family.auth_code)
    
    def test_family_str(self):
        self.assertEqual(str(self.family), "Test Family")

class MemberModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'pass123')
        self.family = Family.objects.create(name="Test Family")
        self.member = Member.objects.create(user=self.user, family=self.family)
    
    def test_member_creation(self):
        self.assertEqual(self.member.user.username, 'testuser')
        self.assertEqual(self.member.family.name, 'Test Family')

class CategoryModelTest(TestCase):
    def setUp(self):
        self.family = Family.objects.create(name="Test Family")
        self.category = Category.objects.create(
            family=self.family,
            name="Groceries",
            type="expense"
        )
    
    def test_category_creation(self):
        self.assertEqual(self.category.name, "Groceries")
        self.assertEqual(self.category.type, "expense")

class LogModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'pass123')
        self.family = Family.objects.create(name="Test Family")
        self.member = Member.objects.create(user=self.user, family=self.family)
        self.category = Category.objects.create(
            family=self.family,
            name="Groceries",
            type="expense"
        )
        self.log = Log.objects.create(
            family=self.family,
            member=self.member,
            category=self.category,
            amount=Decimal('50.00'),
            date=date.today(),
            description="Weekly groceries"
        )
    
    def test_log_creation(self):
        self.assertEqual(self.log.amount, Decimal('50.00'))
        self.assertEqual(self.log.category.name, "Groceries")

class ViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@example.com', 'pass123')
        self.family = Family.objects.create(name="Test Family")
        self.member = Member.objects.create(user=self.user, family=self.family)
    
    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_dashboard_loads_after_login(self):
        self.client.login(username='testuser', password='pass123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')