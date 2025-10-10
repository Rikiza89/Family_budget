# ============================================================================
# family_app/urls.py
# ============================================================================
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('logs/', views.logs_view, name='logs'),
    path('logs/delete/<int:log_id>/', views.delete_log, name='delete_log'),
    path('budget/', views.budget_view, name='budget'),
    path('budget/delete/<int:budget_id>/', views.delete_budget, name='delete_budget'),
    path('recurring/', views.recurring_view, name='recurring'),
    path('recurring/delete/<int:recurring_id>/', views.delete_recurring, name='delete_recurring'),
    path('events/', views.events_view, name='events'),
    path('events/delete/<int:event_id>/', views.delete_event, name='delete_event'),
    path('settings/', views.family_settings, name='family_settings'),
    path('settings/delete-category/<int:category_id>/', views.delete_category, name='delete_category'),
]