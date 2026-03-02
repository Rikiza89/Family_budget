# ============================================================================
# family_app/views.py
# ============================================================================
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings as django_settings
from django.http import JsonResponse
from django.db import IntegrityError
from django.db.models import Sum, Q
from datetime import datetime, timedelta, date
from decimal import Decimal
from .models import Family, Member, Log, Category, BudgetLimit, RecurringLog, FutureEvent
from .forms import LogForm, CategoryForm, BudgetLimitForm, RecurringLogForm, FutureEventForm, DateRangeForm, AIAnalyticsForm

try:
    import anthropic as _anthropic_module
    _ANTHROPIC_AVAILABLE = True
except ImportError:
    _ANTHROPIC_AVAILABLE = False


def get_member_and_family(request):
    """Helper to retrieve the member and family for the current user."""
    member = Member.objects.get(user=request.user)
    return member, member.family


@login_required
def dashboard(request):
    try:
        member, family = get_member_and_family(request)
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

    # Budget alerts and near-warnings
    budget_alerts = []
    budget_warnings = []
    budgets = BudgetLimit.objects.filter(family=family)
    for budget in budgets:
        spent = logs.filter(category=budget.category).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        percentage = float(spent / budget.amount_limit * 100) if budget.amount_limit else 0
        entry = {
            'category': budget.category.name,
            'limit': budget.amount_limit,
            'spent': spent,
            'percentage': min(percentage, 100),
        }
        if percentage >= 100:
            budget_alerts.append(entry)
        elif percentage >= 80:
            budget_warnings.append(entry)

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
        'budget_warnings': budget_warnings,
        'upcoming_events': upcoming_events,
        'month_year': month_start.strftime('%B %Y'),
    }
    return render(request, 'dashboard.html', context)


@login_required
def logs_view(request):
    try:
        member, family = get_member_and_family(request)
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
        log_form.fields['category'].queryset = Category.objects.filter(family=family)
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

    # Compute totals and count for currently filtered logs
    log_count = logs.count()
    filtered_income = logs.filter(category__type='income').aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
    filtered_expense = logs.filter(category__type='expense').aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
    filtered_saving = logs.filter(category__type='saving').aggregate(Sum('amount'))['amount__sum'] or Decimal('0')

    context = {
        'logs': logs[:100],
        'log_count': log_count,
        'log_form': log_form,
        'date_form': form,
        'family': family,
        'filtered_income': filtered_income,
        'filtered_expense': filtered_expense,
        'filtered_saving': filtered_saving,
        'is_truncated': log_count > 100,
    }
    return render(request, 'logs.html', context)


@login_required
def delete_log(request, log_id):
    if request.method != 'POST':
        return redirect('logs')
    try:
        member, family = get_member_and_family(request)
        log = Log.objects.get(id=log_id, family=family)
        log.delete()
        messages.success(request, "Log deleted successfully!")
    except Member.DoesNotExist:
        messages.error(request, "You are not assigned to a family.")
    except Log.DoesNotExist:
        messages.error(request, "Log not found.")
    return redirect('logs')


@login_required
def budget_view(request):
    try:
        member, family = get_member_and_family(request)
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
        percentage = float(spent / budget.amount_limit * 100) if budget.amount_limit else 0

        budget_data.append({
            'budget': budget,
            'spent': spent,
            'remaining': remaining,
            'percentage': min(percentage, 100),
            'over_budget': percentage > 100,
            'status': 'danger' if percentage >= 100 else 'warning' if percentage >= 80 else 'success',
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
            except IntegrityError:
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
    if request.method != 'POST':
        return redirect('budget')
    try:
        member, family = get_member_and_family(request)
        budget = BudgetLimit.objects.get(id=budget_id, family=family)
        budget.delete()
        messages.success(request, "Budget deleted!")
    except Member.DoesNotExist:
        messages.error(request, "You are not assigned to a family.")
    except BudgetLimit.DoesNotExist:
        messages.error(request, "Budget not found.")
    return redirect('budget')


@login_required
def recurring_view(request):
    try:
        member, family = get_member_and_family(request)
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
    if request.method != 'POST':
        return redirect('recurring')
    try:
        member, family = get_member_and_family(request)
        recurring = RecurringLog.objects.get(id=recurring_id, family=family)
        recurring.delete()
        messages.success(request, "Recurring log deleted!")
    except Member.DoesNotExist:
        messages.error(request, "You are not assigned to a family.")
    except RecurringLog.DoesNotExist:
        messages.error(request, "Recurring log not found.")
    return redirect('recurring')


@login_required
def events_view(request):
    try:
        member, family = get_member_and_family(request)
    except Member.DoesNotExist:
        messages.error(request, "You are not assigned to a family.")
        return redirect('login')

    today = date.today()
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
        'today': today,
    }
    return render(request, 'events.html', context)


@login_required
def delete_event(request, event_id):
    if request.method != 'POST':
        return redirect('events')
    try:
        member, family = get_member_and_family(request)
        event = FutureEvent.objects.get(id=event_id, family=family)
        event.delete()
        messages.success(request, "Event deleted!")
    except Member.DoesNotExist:
        messages.error(request, "You are not assigned to a family.")
    except FutureEvent.DoesNotExist:
        messages.error(request, "Event not found.")
    return redirect('events')


@login_required
def family_settings(request):
    try:
        member, family = get_member_and_family(request)
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
            except IntegrityError:
                messages.error(request, "A category with that name already exists.")
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
    if request.method != 'POST':
        return redirect('family_settings')
    try:
        member, family = get_member_and_family(request)
        category = Category.objects.get(id=category_id, family=family)
        category.delete()
        messages.success(request, "Category deleted!")
    except Member.DoesNotExist:
        messages.error(request, "You are not assigned to a family.")
    except Category.DoesNotExist:
        messages.error(request, "Category not found.")
    return redirect('family_settings')


# ============================================================================
# AI Analytics
# ============================================================================

def _months_ago(n):
    """Return the first day of the month N months before today."""
    today = date.today()
    month = today.month - n
    year = today.year
    while month <= 0:
        month += 12
        year -= 1
    return date(year, month, 1)


def _collect_analytics_data(family, start_date, end_date):
    """Build a structured financial summary for the given date range."""
    logs = Log.objects.filter(
        family=family, date__range=[start_date, end_date]
    ).select_related('category')

    income_total = logs.filter(category__type='income').aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
    expense_total = logs.filter(category__type='expense').aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
    saving_total = logs.filter(category__type='saving').aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
    balance = income_total - expense_total - saving_total

    # Month-by-month breakdown in chronological order
    monthly = []
    cursor = start_date.replace(day=1)
    while cursor <= end_date:
        next_month = (cursor + timedelta(days=32)).replace(day=1)
        month_end = min(next_month - timedelta(days=1), end_date)
        month_logs = logs.filter(date__range=[cursor, month_end])
        m_income = month_logs.filter(category__type='income').aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        m_expense = month_logs.filter(category__type='expense').aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        m_saving = month_logs.filter(category__type='saving').aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        if m_income or m_expense or m_saving:
            monthly.append({
                'label': cursor.strftime('%b %Y'),
                'income': m_income,
                'expense': m_expense,
                'saving': m_saving,
                'balance': m_income - m_expense - m_saving,
            })
        cursor = next_month

    # Category breakdown
    category_breakdown = []
    for cat in Category.objects.filter(family=family):
        total = logs.filter(category=cat).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        if total > 0:
            category_breakdown.append({'name': cat.name, 'type': cat.type, 'total': total})

    # Current-month budget performance
    today = date.today()
    cm_start = today.replace(day=1)
    cm_end = (cm_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    cm_logs = Log.objects.filter(family=family, date__range=[cm_start, cm_end])
    budget_performance = []
    for budget in BudgetLimit.objects.filter(family=family).select_related('category'):
        spent = cm_logs.filter(category=budget.category).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        pct = float(spent / budget.amount_limit * 100) if budget.amount_limit else 0
        budget_performance.append({
            'category': budget.category.name,
            'limit': budget.amount_limit,
            'spent': spent,
            'percentage': pct,
            'status': 'Over budget' if pct >= 100 else 'Approaching limit' if pct >= 80 else 'On track',
        })

    return {
        'start_date': start_date,
        'end_date': end_date,
        'income_total': income_total,
        'expense_total': expense_total,
        'saving_total': saving_total,
        'balance': balance,
        'monthly': monthly,
        'category_breakdown': category_breakdown,
        'budget_performance': budget_performance,
        'transaction_count': logs.count(),
    }


def _build_prompt(data, topics, custom_question):
    """Compose the AI prompt from collected financial data and user options."""
    topic_labels = {
        'spending': 'spending breakdown and patterns',
        'budget': 'budget performance and adherence',
        'savings': 'savings progress and whether the family is saving enough',
        'income': 'income trends and stability',
        'cashflow': 'cash flow (income vs expenses month by month)',
        'recommendations': 'specific, actionable recommendations to improve financial health',
    }
    selected = [topic_labels[t] for t in topics if t in topic_labels]

    lines = [
        "You are a helpful, friendly personal finance advisor. "
        "Analyze the family budget data below and provide clear, practical insights.",
        "",
        f"## Financial Data: {data['start_date'].strftime('%b %d, %Y')} – {data['end_date'].strftime('%b %d, %Y')}",
        "",
        "### Period Summary",
        f"- Total Income:   ${data['income_total']:>10,.2f}",
        f"- Total Expenses: ${data['expense_total']:>10,.2f}",
        f"- Total Savings:  ${data['saving_total']:>10,.2f}",
        f"- Net Balance:    ${data['balance']:>10,.2f}",
        f"- Transactions recorded: {data['transaction_count']}",
        "",
    ]

    if data['monthly']:
        lines += ["### Month-by-Month Breakdown",
                  "| Month | Income | Expenses | Savings | Balance |",
                  "|-------|-------:|---------:|--------:|--------:|"]
        for m in data['monthly']:
            lines.append(
                f"| {m['label']} | ${m['income']:,.2f} | ${m['expense']:,.2f} | "
                f"${m['saving']:,.2f} | ${m['balance']:,.2f} |"
            )
        lines.append("")

    expenses = [c for c in data['category_breakdown'] if c['type'] == 'expense']
    incomes  = [c for c in data['category_breakdown'] if c['type'] == 'income']
    savings  = [c for c in data['category_breakdown'] if c['type'] == 'saving']

    if expenses:
        total_exp = data['expense_total'] or Decimal('1')
        lines += ["### Expense Categories",
                  "| Category | Amount | % of Expenses |",
                  "|----------|-------:|-------------:|"]
        for c in sorted(expenses, key=lambda x: x['total'], reverse=True):
            pct = float(c['total'] / total_exp * 100)
            lines.append(f"| {c['name']} | ${c['total']:,.2f} | {pct:.1f}% |")
        lines.append("")

    if incomes:
        lines += ["### Income Sources",
                  "| Source | Amount |",
                  "|--------|-------:|"]
        for c in sorted(incomes, key=lambda x: x['total'], reverse=True):
            lines.append(f"| {c['name']} | ${c['total']:,.2f} |")
        lines.append("")

    if savings:
        lines.append("### Savings")
        for c in savings:
            lines.append(f"- {c['name']}: ${c['total']:,.2f}")
        lines.append("")

    if data['budget_performance']:
        lines += ["### Current Month Budget Performance",
                  "| Category | Limit | Spent | Used | Status |",
                  "|----------|------:|------:|-----:|--------|"]
        for b in data['budget_performance']:
            lines.append(
                f"| {b['category']} | ${b['limit']:,.2f} | ${b['spent']:,.2f} "
                f"| {b['percentage']:.0f}% | {b['status']} |"
            )
        lines.append("")

    if selected:
        lines.append(f"### Please analyze: {', '.join(selected)}.")
        lines.append("")

    if custom_question:
        lines.append(f"### Specific question from the family:")
        lines.append(custom_question)
        lines.append("")

    lines.append(
        "Respond with clear markdown (use ## headings, bullet points, **bold** for numbers). "
        "Be specific — reference actual dollar amounts and percentages from the data above. "
        "Keep the tone friendly and encouraging."
    )
    return "\n".join(lines)


@login_required
def ai_analytics(request):
    try:
        member, family = get_member_and_family(request)
    except Member.DoesNotExist:
        messages.error(request, "You are not assigned to a family.")
        return redirect('login')

    form = AIAnalyticsForm()

    if request.method == 'POST':
        # AJAX call from the analytics page
        form = AIAnalyticsForm(request.POST)
        if not form.is_valid():
            errors = {f: e.as_text() for f, e in form.errors.items()}
            return JsonResponse({'error': 'Please fix the form errors.', 'field_errors': errors}, status=400)

        cd = form.cleaned_data
        today = date.today()

        if cd['period'] == 'custom':
            start_date = cd['custom_start']
            end_date = cd['custom_end']
        else:
            months_back = int(cd['period'])
            start_date = _months_ago(months_back)
            end_date = today

        topics = cd.get('topics') or []
        custom_question = cd.get('custom_question', '').strip()

        # Require at least one topic or a custom question
        if not topics and not custom_question:
            return JsonResponse(
                {'error': 'Please select at least one topic or enter a custom question.'},
                status=400,
            )

        data = _collect_analytics_data(family, start_date, end_date)

        if data['transaction_count'] == 0:
            return JsonResponse(
                {'error': f'No transactions found between {start_date.strftime("%b %d, %Y")} '
                          f'and {end_date.strftime("%b %d, %Y")}. Add some logs first.'},
                status=400,
            )

        if not _ANTHROPIC_AVAILABLE:
            return JsonResponse(
                {'error': 'The anthropic package is not installed. Run: pip install anthropic'},
                status=503,
            )

        api_key = django_settings.ANTHROPIC_API_KEY
        if not api_key:
            return JsonResponse(
                {'error': 'ANTHROPIC_API_KEY is not configured. '
                          'Add it to your .env file and restart the server.'},
                status=503,
            )

        prompt = _build_prompt(data, topics, custom_question)

        try:
            client = _anthropic_module.Anthropic(api_key=api_key)
            response = client.messages.create(
                model='claude-haiku-4-5-20251001',
                max_tokens=2048,
                system=(
                    "You are a helpful personal finance advisor for a family budget app. "
                    "Provide concise, actionable analysis in markdown format."
                ),
                messages=[{'role': 'user', 'content': prompt}],
            )
            analysis_text = response.content[0].text
        except Exception as exc:
            return JsonResponse({'error': f'AI service error: {exc}'}, status=502)

        return JsonResponse({
            'analysis': analysis_text,
            'period': f"{start_date.strftime('%b %d, %Y')} – {end_date.strftime('%b %d, %Y')}",
            'transaction_count': data['transaction_count'],
        })

    return render(request, 'ai_analytics.html', {'form': form, 'family': family})
