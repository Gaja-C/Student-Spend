from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from rango.models import UserProfile
from rango.forms import UserForm, UserProfileForm
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from django.contrib import messages
from .models import ExpenseCategory, Expense
from datetime import date

# Create your views here.
def index(request):
    return render(request, 'rango/index.html')

def about(request):
    return HttpResponse("Rango says here is the about page. </br><a href='/rango/'>Index</a>")

def registration(request):
    registered = False

    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            profile.save()
            registered = True
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
    return render(request, 'rango/registration.html', context={'user_form': user_form, 'profile_form': profile_form, 'registered': registered})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return redirect(reverse('rango:index'))
            else:
                return HttpResponse("Your Rango account is disabled.")
        else:
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied.")
    else:
        return render(request, 'rango/login.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse('rango:index'))
    
@login_required 
def budget(request):
    return render(request, 'rango/budget.html')

@login_required 
def dashboard(request):
    return render(request, 'rango/dashboard.html')

@login_required 
def expenses(request):
    profile = request.user.userprofile

    categories = ExpenseCategory.objects.filter(user=profile).order_by('lastAddedTo').values().reverse()
    categories = categories[:3]
    mostRecentData = []
    for category in categories:
        microExpenses = Expense.objects.filter(user=profile, category_id = category['id']).order_by('date').values().reverse()
        microExpenses = microExpenses[:3]
        mostRecentData.append({'category' : category, 'expenses' : microExpenses})

    if request.method == 'POST':
        action = request.POST.get("action")
        if action == "add_category":
            categoryName = request.POST.get('categoryName')
            if (ExpenseCategory.objects.filter(user=profile, name=categoryName).exists()):
                messages.error(request, "Category of same name already exists.")
            else:
                ExpenseCategory.objects.create(user=profile, name=categoryName)
            return redirect(reverse('rango:expenses'))
        elif action == "remove_category":
            categoryName = request.POST.get('categoryName')
            if (ExpenseCategory.objects.filter(user=profile, name=categoryName).exists()):
                ExpenseCategory.objects.filter(user=profile, name=categoryName).delete()
            else:
                messages.error(request, "Chosen category does not exist.")
        elif action == "add_expense":
            expenseName = request.POST.get('expenseName')
            categoryName = request.POST.get('categoryName')
            amount = request.POST.get('amount')
            dateOf = request.POST.get('date')
            category = ExpenseCategory.objects.filter(user=profile, name=categoryName)
            if category.exists():
                if (Expense.objects.filter(user=profile, name=expenseName, category=category.get(), date=dateOf).exists()):
                    messages.error(request, "Expense of same name and date already exists in chosen category.")
                else:
                    Expense.objects.create(user=profile, name=expenseName, category=category.get(), amount=amount, date=dateOf)
            else:
                messages.error(request, "Chosen expense does not exist.")
        else:
            expenseName = request.POST.get('expenseName')
            categoryName = request.POST.get('categoryName')
            dateOf = request.POST.get('date')
            category = ExpenseCategory.objects.filter(user=profile, name=categoryName)
            if category.exists():
                if (Expense.objects.filter(user=profile, name=expenseName, category=category.get(), date=dateOf).exists()):
                    Expense.objects.filter(user=profile, name=expenseName, category=category.get(), date=dateOf).delete()
                else:
                    messages.error(request, "Chosen expense does not exist.")
            else:
                messages.error(request, "Chosen category does not exist.")
    return render(request, 'rango/expenses.html', {'mostRecentData' : mostRecentData},)

@login_required 
def bill_splitting(request):
    return render(request, 'rango/bill-splitting.html')

@login_required
def add_money(request):
    if request.method == 'POST':
        pounds = request.POST.get('pounds')
        pence = request.POST.get('pence').zfill(2)
        try:
            total = (pounds)+"."+(pence)
            total = Decimal(total).quantize(Decimal("0.00"))
            profile = request.user.userprofile
            profile.money += total
            profile.save()
            return redirect(reverse('rango:index'))
        except:
            return HttpResponse("Invalid input supplied.")
    return render(request, 'rango/add-money.html')

@login_required
def remove_money(request):
    if request.method == 'POST':
        pounds = request.POST.get('pounds')
        pence = request.POST.get('pence').zfill(2)
        try:
            total = (pounds)+"."+(pence)
            total = Decimal(total).quantize(Decimal("0.00"))
            profile = request.user.userprofile
            if total > profile.money:
                messages.error(request, "Input must be less than money already stored.")
                return redirect(reverse('rango:remove_money'))
            else:
                profile.money -= total
                profile.save()
                return redirect(reverse('rango:index'))
        except:
            messages.error(request, "Invalid input supplied.")
    return render(request, 'rango/remove-money.html')