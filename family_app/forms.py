# ============================================================================
# family_app/forms.py
# ============================================================================
from django import forms
from django.core.validators import MinValueValidator
from .models import Log, Category, BudgetLimit, RecurringLog, FutureEvent
from datetime import date
from decimal import Decimal


class LogForm(forms.ModelForm):
    class Meta:
        model = Log
        fields = ['category', 'amount', 'date', 'description']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional note'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.initial.get('date') and not self.data.get('date'):
            self.fields['date'].initial = date.today()

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is not None and amount <= Decimal('0'):
            raise forms.ValidationError("Amount must be greater than zero.")
        return amount


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'type']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Groceries'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
        }


class BudgetLimitForm(forms.ModelForm):
    class Meta:
        model = BudgetLimit
        fields = ['category', 'amount_limit']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'amount_limit': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
        }

    def clean_amount_limit(self):
        amount = self.cleaned_data.get('amount_limit')
        if amount is not None and amount <= Decimal('0'):
            raise forms.ValidationError("Budget limit must be greater than zero.")
        return amount


class RecurringLogForm(forms.ModelForm):
    class Meta:
        model = RecurringLog
        fields = ['category', 'amount', 'description', 'recurrence', 'start_date', 'end_date', 'active']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional note'}),
            'recurrence': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is not None and amount <= Decimal('0'):
            raise forms.ValidationError("Amount must be greater than zero.")
        return amount

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError("End date cannot be before start date.")
        return cleaned_data


class FutureEventForm(forms.ModelForm):
    class Meta:
        model = FutureEvent
        fields = ['name', 'amount', 'event_date', 'type', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Annual insurance payment'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'event_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional note'}),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is not None and amount <= Decimal('0'):
            raise forms.ValidationError("Amount must be greater than zero.")
        return amount


class AIAnalyticsForm(forms.Form):
    PERIOD_CHOICES = [
        ('1', 'Last month'),
        ('3', 'Last 3 months'),
        ('6', 'Last 6 months'),
        ('12', 'Last year'),
        ('custom', 'Custom range'),
    ]

    TOPIC_CHOICES = [
        ('spending', 'Spending breakdown'),
        ('budget', 'Budget performance'),
        ('savings', 'Savings progress'),
        ('income', 'Income trends'),
        ('cashflow', 'Cash flow analysis'),
        ('recommendations', 'Recommendations & tips'),
    ]

    period = forms.ChoiceField(
        choices=PERIOD_CHOICES,
        initial='3',
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='Analysis period',
    )
    custom_start = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='From',
    )
    custom_end = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='To',
    )
    topics = forms.MultipleChoiceField(
        choices=TOPIC_CHOICES,
        initial=['spending', 'budget', 'recommendations'],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label='Topics to analyze',
        required=False,
    )
    custom_question = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'e.g. "How can we cut our grocery bill?" or "Are we saving enough?"',
        }),
        label='Custom question (optional)',
    )

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('period') == 'custom':
            start = cleaned_data.get('custom_start')
            end = cleaned_data.get('custom_end')
            if not start:
                self.add_error('custom_start', 'Required for custom range.')
            if not end:
                self.add_error('custom_end', 'Required for custom range.')
            if start and end and end < start:
                raise forms.ValidationError('End date cannot be before start date.')
        return cleaned_data


class DateRangeForm(forms.Form):
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='From'
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='To'
    )

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_date')
        end = cleaned_data.get('end_date')
        if start and end and end < start:
            raise forms.ValidationError("End date cannot be before start date.")
        return cleaned_data
