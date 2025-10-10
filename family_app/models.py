# ============================================================================
# family_app/models.py
# ============================================================================
from django.db import models
import uuid
from datetime import date
from django.conf import settings

class Family(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Family Name")
    auth_code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="Authorization Code")

    class Meta:
        verbose_name_plural = "Families"
        ordering = ['name']

    def __str__(self):
        return self.name

class Member(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="User Account")
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='members', verbose_name="Family")

    class Meta:
        ordering = ['user__username']
        unique_together = ('user', 'family')

    def __str__(self):
        return f"{self.user.username} ({self.family.name})"

class Category(models.Model):
    CATEGORY_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
        ('saving', 'Saving'),
    ]
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='categories', verbose_name="Family")
    name = models.CharField(max_length=100, verbose_name="Category Name")
    type = models.CharField(max_length=10, choices=CATEGORY_TYPES, verbose_name="Category Type")

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['family__name', 'name']
        unique_together = ('family', 'name')

    def __str__(self):
        return f"{self.name} ({self.type.capitalize()}) - {self.family.name}"

class Log(models.Model):
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='logs', verbose_name="Family")
    member = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Logged By")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='logs', verbose_name="Category")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Amount")
    date = models.DateField(verbose_name="Date")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    class Meta:
        verbose_name_plural = "Logs"
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.date} - {self.category.name}: {self.amount}"

class RecurringLog(models.Model):
    RECURRENCE_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('bi-weekly', 'Bi-Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annually', 'Annually'),
    ]
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='recurring_logs', verbose_name="Family")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='recurring_logs', verbose_name="Category")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Amount")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    recurrence = models.CharField(max_length=20, choices=RECURRENCE_CHOICES, verbose_name="Recurrence Pattern")
    start_date = models.DateField(default=date.today, verbose_name="Start Date")
    end_date = models.DateField(null=True, blank=True, verbose_name="End Date (Optional)")
    active = models.BooleanField(default=True, verbose_name="Is Active?")

    class Meta:
        verbose_name_plural = "Recurring Logs"
        ordering = ['-start_date', 'category__name']

    def __str__(self):
        return f"Recurring: {self.category.name} - {self.amount} ({self.recurrence})"

class BudgetLimit(models.Model):
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='budget_limits', verbose_name="Family")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='budget_limits', verbose_name="Category")
    amount_limit = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Monthly Limit")
    period = models.CharField(max_length=20, default='monthly', verbose_name="Limit Period")

    class Meta:
        verbose_name_plural = "Budget Limits"
        unique_together = ('family', 'category', 'period')
        ordering = ['family__name', 'category__name']

    def __str__(self):
        return f"{self.family.name} - {self.category.name} limit: ${self.amount_limit} per {self.period}"

class FutureEvent(models.Model):
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='future_events')
    name = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    event_date = models.DateField()
    type = models.CharField(max_length=10, choices=[('income', 'Income'), ('expense', 'Expense')])
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['event_date', 'created_at']

    def __str__(self):
        return f"{self.name} ({self.type}): ${self.amount} on {self.event_date}"