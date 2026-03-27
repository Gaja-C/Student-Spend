from django.urls import path
from django.urls import path
from student_spend import views
from django.contrib import admin

app_name = 'student_spend' #we should probaby chnage that name 
urlpatterns = [
    path('', views.index, name='index'),
    path('budget/', views.budget, name='budget'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.user_login, name='login'),
    path('registration/', views.registration, name='registration'),
    path('logout/', views.user_logout, name='logout'),
    path('expenses/', views.expenses, name='expenses'),
    path('bill_splitting/', views.bill_splitting, name='bill_splitting'),
    path('add_money/', views.add_money, name="add_money"),
    path('remove_money/', views.remove_money, name="remove_money"),
    path('view_all_expenses/', views.view_all_expenses, name="view_all_expenses"),
    path('view_all_groups/', views.view_all_groups, name="view_all_groups"),
    path('view_all_budgets/', views.view_all_budgets, name="view_all_budgets"),
    path('budget/edit-goal/', views.edit_goal, name="edit_goal"),
]