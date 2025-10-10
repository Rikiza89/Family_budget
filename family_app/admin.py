# ============================================================================
# family_app/admin.py
# ============================================================================
from django.contrib import admin
from .models import Family, Member, Category, Log, RecurringLog, BudgetLimit, FutureEvent

@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    list_display = ('name', 'auth_code', 'member_count')
    search_fields = ('name',)
    readonly_fields = ('auth_code',)
    
    def member_count(self, obj):
        return obj.members.count()
    member_count.short_description = 'Members'

# @admin.register(Member)
# class MemberAdmin(admin.ModelAdmin):
#     list_display = ('user', 'family')
#     list_filter = ('family',)
#     search_fields = ('user__username', 'family__name')
#     readonly_fields = ('user',)

@admin.register(Member)   
class MemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'family')

    def save_model(self, request, obj, form, change):
        if not obj.user:
            # Example: create a dummy user automatically
            from django.contrib.auth.models import User
            obj.user = User.objects.create(username=f"member_{obj.family.id}_{User.objects.count()+1}")
        super().save_model(request, obj, form, change)
        
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'family')
    list_filter = ('type', 'family')
    search_fields = ('name', 'family__name')

@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ('date', 'category', 'amount', 'family', 'member')
    list_filter = ('date', 'category__type', 'family')
    search_fields = ('category__name', 'family__name', 'description')
    date_hierarchy = 'date'
    readonly_fields = ('created_at', 'family')
    
    fieldsets = (
        ('Transaction Info', {
            'fields': ('family', 'member', 'category', 'amount', 'date')
        }),
        ('Details', {
            'fields': ('description', 'created_at')
        }),
    )

@admin.register(RecurringLog)
class RecurringLogAdmin(admin.ModelAdmin):
    list_display = ('category', 'amount', 'recurrence', 'active', 'family')
    list_filter = ('recurrence', 'active', 'family')
    search_fields = ('category__name', 'family__name')
    
    fieldsets = (
        ('Recurring Transaction', {
            'fields': ('family', 'category', 'amount', 'description')
        }),
        ('Schedule', {
            'fields': ('recurrence', 'start_date', 'end_date', 'active')
        }),
    )

@admin.register(BudgetLimit)
class BudgetLimitAdmin(admin.ModelAdmin):
    list_display = ('family', 'category', 'amount_limit', 'period')
    list_filter = ('period', 'family')
    search_fields = ('family__name', 'category__name')
    
    fieldsets = (
        ('Budget Setting', {
            'fields': ('family', 'category', 'amount_limit', 'period')
        }),
    )

@admin.register(FutureEvent)
class FutureEventAdmin(admin.ModelAdmin):
    list_display = ('name', 'event_date', 'type', 'amount', 'family')
    list_filter = ('type', 'event_date', 'family')
    search_fields = ('name', 'family__name')
    date_hierarchy = 'event_date'
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Event Info', {
            'fields': ('family', 'name', 'type', 'amount')
        }),
        ('Details', {
            'fields': ('description', 'event_date', 'created_at')
        }),
    )