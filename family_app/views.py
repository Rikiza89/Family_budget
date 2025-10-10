# ============================================================================
# family_app/views.py
# ============================================================================
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Q
from datetime import datetime, timedelta, date
from decimal import Decimal
from .models import Family, Member, Log, Category, BudgetLimit, RecurringLog, FutureEvent
from .forms import LogForm, CategoryForm, BudgetLimitForm, RecurringLogForm, FutureEventForm, DateRangeForm

@login_required
def dashboard(request):
    try:
        member = Member.objects.get(user=request.user)
        family = member.family
    except Member.DoesNotExist:
        messages.error(request, "You are not assigned to a family.")
        return redirect('login')

    today = date.today()
    month_start = today.replace(day=1)
    month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

    # Get logs for current month
    logs = Log.objects.filter(family=family, date__range=[month_start, month_end])
    
    # Calculate totals
    income_total = logs.filter(category__type='income').aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
    expense_total = logs.filter(category__type='expense').aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
    saving_total = logs.filter(category__type='saving').aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
    balance = income_total - expense_total - saving_total

    # Category breakdown
    categories = Category.objects.filter(family=family)
    category_data = []
    for cat in categories:
        total = logs.filter(category=cat).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        if total != 0:
            category_data.append({'name': cat.name, 'type': cat.type, 'total': total})

    # Budget alerts
    budget_alerts = []
    budgets = BudgetLimit.objects.filter(family=family)
    for budget in budgets:
        spent = logs.filter(category=budget.category).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        if spent >= budget.amount_limit:
            budget_alerts.append({
                'category': budget.category.name,
                'limit': budget.amount_limit,
                'spent': spent,
                'percentage': (spent / budget.amount_limit * 100) if budget.amount_limit else 0
            })

    # Upcoming events
    upcoming_events = FutureEvent.objects.filter(
        family=family,
        event_date__gte=today,
        event_date__lte=today + timedelta(days=30)
    ).order_by('event_date')[:5]

    context = {
        'family': family,
        'income_total': income_total,
        'expense_total': expense_total,
        'saving_total': saving_total,
        'balance': balance,
        'category_data': category_data,
        'budget_alerts': budget_alerts,
        'upcoming_events': upcoming_events,
        'month_year': month_start.strftime('%B %Y'),
    }
    return render(request, 'dashboard.html', context)

@login_required
def logs_view(request):
    try:
        member = Member.objects.get(user=request.user)
        family = member.family
    except Member.DoesNotExist:
        messages.error(request, "You are not assigned to a family.")
        return redirect('login')

    form = DateRangeForm(request.GET or None)
    logs = Log.objects.filter(family=family)

    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        if start_date:
            logs = logs.filter(date__gte=start_date)
        if end_date:
            logs = logs.filter(date__lte=end_date)

    if request.method == 'POST':
        log_form = LogForm(request.POST)
        if log_form.is_valid():
            log = log_form.save(commit=False)
            log.family = family
            log.member = member
            log.save()
            messages.success(request, "Log added successfully!")
            return redirect('logs')
    else:
        log_form = LogForm()

    categories = Category.objects.filter(family=family)
    log_form.fields['category'].queryset = categories

    context = {
        'logs': logs[:100],
        'log_form': log_form,
        'date_form': form,
        'family': family,
    }
    return render(request, 'logs.html', context)

@login_required
def delete_log(request, log_id):
    try:
        member = Member.objects.get(user=request.user)
        family = member.family
        log = Log.objects.get(id=log_id, family=family)
        log.delete()
        messages.success(request, "Log deleted successfully!")
    except (Member.DoesNotExist, Log.DoesNotExist):
        messages.error(request, "Log not found.")
    return redirect('logs')

@login_required
def budget_view(request):
    try:
        member = Member.objects.get(user=request.user)
        family = member.family
    except Member.DoesNotExist:
        messages.error(request, "You are not assigned to a family.")
        return redirect('login')

    budgets = BudgetLimit.objects.filter(family=family)
    today = date.today()
    month_start = today.replace(day=1)
    month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

    budget_data = []
    for budget in budgets:
        spent = Log.objects.filter(
            family=family,
            category=budget.category,
            date__range=[month_start, month_end]
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        
        remaining = budget.amount_limit - spent
        percentage = (spent / budget.amount_limit * 100) if budget.amount_limit else 0
        
        budget_data.append({
            'budget': budget,
            'spent': spent,
            'remaining': remaining,
            'percentage': percentage,
            'status': 'danger' if percentage >= 100 else 'warning' if percentage >= 80 else 'success'
        })

    if request.method == 'POST':
        budget_form = BudgetLimitForm(request.POST)
        categories = Category.objects.filter(family=family)
        budget_form.fields['category'].queryset = categories
        
        if budget_form.is_valid():
            budget = budget_form.save(commit=False)
            budget.family = family
            try:
                budget.save()
                messages.success(request, "Budget limit added!")
                return redirect('budget')
            except:
                messages.error(request, "This category already has a budget limit.")
    else:
        budget_form = BudgetLimitForm()
        categories = Category.objects.filter(family=family)
        budget_form.fields['category'].queryset = categories

    context = {
        'budget_data': budget_data,
        'budget_form': budget_form,
        'family': family,
    }
    return render(request, 'budget.html', context)

@login_required
def delete_budget(request, budget_id):
    try:
        member = Member.objects.get(user=request.user)
        family = member.family
        budget = BudgetLimit.objects.get(id=budget_id, family=family)
        budget.delete()
        messages.success(request, "Budget deleted!")
    except (Member.DoesNotExist, BudgetLimit.DoesNotExist):
        messages.error(request, "Budget not found.")
    return redirect('budget')

@login_required
def recurring_view(request):
    try:
        member = Member.objects.get(user=request.user)
        family = member.family
    except Member.DoesNotExist:
        messages.error(request, "You are not assigned to a family.")
        return redirect('login')

    recurring = RecurringLog.objects.filter(family=family)

    if request.method == 'POST':
        rec_form = RecurringLogForm(request.POST)
        categories = Category.objects.filter(family=family)
        rec_form.fields['category'].queryset = categories
        
        if rec_form.is_valid():
            rec = rec_form.save(commit=False)
            rec.family = family
            rec.save()
            messages.success(request, "Recurring log added!")
            return redirect('recurring')
    else:
        rec_form = RecurringLogForm()
        categories = Category.objects.filter(family=family)
        rec_form.fields['category'].queryset = categories

    context = {
        'recurring': recurring,
        'rec_form': rec_form,
        'family': family,
    }
    return render(request, 'recurring.html', context)

@login_required
def delete_recurring(request, recurring_id):
    try:
        member = Member.objects.get(user=request.user)
        family = member.family
        recurring = RecurringLog.objects.get(id=recurring_id, family=family)
        recurring.delete()
        messages.success(request, "Recurring log deleted!")
    except (Member.DoesNotExist, RecurringLog.DoesNotExist):
        messages.error(request, "Recurring log not found.")
    return redirect('recurring')

@login_required
def events_view(request):
    try:
        member = Member.objects.get(user=request.user)
        family = member.family
    except Member.DoesNotExist:
        messages.error(request, "You are not assigned to a family.")
        return redirect('login')

    events = FutureEvent.objects.filter(family=family).order_by('event_date')

    if request.method == 'POST':
        event_form = FutureEventForm(request.POST)
        if event_form.is_valid():
            event = event_form.save(commit=False)
            event.family = family
            event.save()
            messages.success(request, "Event added!")
            return redirect('events')
    else:
        event_form = FutureEventForm()

    context = {
        'events': events,
        'event_form': event_form,
        'family': family,
    }
    return render(request, 'events.html', context)

@login_required
def delete_event(request, event_id):
    try:
        member = Member.objects.get(user=request.user)
        family = member.family
        event = FutureEvent.objects.get(id=event_id, family=family)
        event.delete()
        messages.success(request, "Event deleted!")
    except (Member.DoesNotExist, FutureEvent.DoesNotExist):
        messages.error(request, "Event not found.")
    return redirect('events')

@login_required
def family_settings(request):
    try:
        member = Member.objects.get(user=request.user)
        family = member.family
    except Member.DoesNotExist:
        messages.error(request, "You are not assigned to a family.")
        return redirect('login')

    members = family.members.all()
    categories = Category.objects.filter(family=family)

    if request.method == 'POST':
        cat_form = CategoryForm(request.POST)
        if cat_form.is_valid():
            category = cat_form.save(commit=False)
            category.family = family
            try:
                category.save()
                messages.success(request, "Category added!")
                return redirect('family_settings')
            except:
                messages.error(request, "Category already exists!")
    else:
        cat_form = CategoryForm()

    context = {
        'family': family,
        'members': members,
        'categories': categories,
        'cat_form': cat_form,
    }
    return render(request, 'family_settings.html', context)

@login_required
def delete_category(request, category_id):
    try:
        member = Member.objects.get(user=request.user)
        family = member.family
        category = Category.objects.get(id=category_id, family=family)
        category.delete()
        messages.success(request, "Category deleted!")
    except (Member.DoesNotExist, Category.DoesNotExist):
        messages.error(request, "Category not found.")
    return redirect('family_settings')