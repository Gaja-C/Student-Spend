from django.contrib import admin
from .models import UserProfile, ExpenseCategory, Expense, Goal, Group, MemberOfGroup

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(ExpenseCategory)
admin.site.register(Expense)
admin.site.register(Goal)
admin.site.register(Group)
admin.site.register(MemberOfGroup)