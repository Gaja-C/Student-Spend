from django.urls import path
from django.conf.urls import url
from rango import views

app_name = 'rango'
urlpatterns = [
    path('', views.index, name='index'),
    path('budget/', views.budget, name='budget'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.user_login, name='login'),
    path('registration/', views.registration, name='registration'),
    path('expenses/', views.expenses, name='expenses'),
    path('bill_splitting/', views.bill_splitting, name='bill-splitting'),
]