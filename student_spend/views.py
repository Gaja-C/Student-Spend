from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from student_spend.models import UserProfile, User
from student_spend.forms import UserForm, UserProfileForm
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from django.contrib import messages
from .models import ExpenseCategory, Expense ,MemberOfGroup,Group, Goal
from datetime import date, datetime
import json

# Create your views here.
def index(request):
    return render(request, 'student_spend/index.html')

def about(request):
    return HttpResponse("Rango says here is the about page. </br><a href='/student_spend/'>Index</a>") # was not sure to change this to student_spend aswell 

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
    return render(request, 'student_spend/registration.html', context={'user_form': user_form, 'profile_form': profile_form, 'registered': registered})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return redirect(reverse('student_spend:index'))
            else:
                return HttpResponse("Your Student_spend account is disabled.")
        else:
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied.")
    else:
        return render(request, 'student_spend/login.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse('student_spend:index'))
    
@login_required 
def budget(request):
    profile = request.user.userprofile
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "add_goal":
            goalName = request.POST.get("goalName")
            date = request.POST.get("date")
            if (not date):
                messages.error(request, "Please enter a date.")
            elif (Goal.objects.filter(user=profile, name=goalName).exists()):
                messages.error(request, "Goal of same name already exists. Please give this goal a more unique name")
            else:
                budget = request.POST.get("amount")
                Goal.objects.create(user=profile, name=goalName, budget=budget, current_amount=0, date=date)
        elif action == "remove_goal":
            goalName = request.POST.get("goalName")
            date = request.POST.get("date")
            if (not(Goal.objects.filter(user=profile, name=goalName, date=date).exists())):
                messages.error(request, "Goal of entered name and date does not exist. Could not remove this goal.")
            else:
                Goal.objects.get(user=profile, name=goalName, date=date).delete()
        elif action == "edit_goal":
            goalName = request.POST.get("goalName")
            addOrSub = Decimal(request.POST.get("amount"))
            goal = Goal.objects.get(user=profile, name=goalName)
            newTotal = goal.current_amount + addOrSub
            if newTotal < 0:
                messages.error(request, "Cannot remove more money than possible. Please enter a valid value to subtract")
            else:
                if newTotal >= goal.budget:
                    goal.delete()
                else:
                    goal.current_amount = newTotal
                    goal.save()

    goals = Goal.objects.filter(user=profile).order_by('date')
    mostRecentData = goals.values()[:3]
    return render(request, 'student_spend/budget.html', {'goals' : goals, 'mostRecentData' : mostRecentData},)

@login_required 
def dashboard(request):
    return render(request, 'student_spend/dashboard.html')

@login_required 
def expenses(request):
    profile = request.user.userprofile

    if request.method == 'POST':
        action = request.POST.get("action")
        if action == "add_category":
            categoryName = request.POST.get('categoryName')
            if (ExpenseCategory.objects.filter(user=profile, name=categoryName).exists()):
                messages.error(request, "Category of same name already exists.")
            else:
                ExpenseCategory.objects.create(user=profile, name=categoryName)
            return redirect(reverse('student_spend:expenses'))
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
            if (not dateOf):
                messages.error(request, "Please enter a date.")
            elif category.exists():
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
            if (not dateOf):
                messages.error(request, "Please enter a date.")
            elif category.exists():
                if (Expense.objects.filter(user=profile, name=expenseName, category=category.get(), date=dateOf).exists()):
                    Expense.objects.filter(user=profile, name=expenseName, category=category.get(), date=dateOf).delete()
                else:
                    messages.error(request, "Chosen expense does not exist.")
            else:
                messages.error(request, "Chosen category does not exist.")
    categories = ExpenseCategory.objects.filter(user=profile).order_by('lastAddedTo').values().reverse()
    allData = []
    for category in categories:
        microExpenses = Expense.objects.filter(user=profile, category_id = category['id']).order_by('date').values().reverse()
        allData.append({'category' : category, 'expenses' : microExpenses})
    categories = categories[:3]
    mostRecentData = []
    for category in categories:
        microExpenses = Expense.objects.filter(user=profile, category_id = category['id']).order_by('date').values().reverse()
        microExpenses = microExpenses[:3]
        mostRecentData.append({'category' : category, 'expenses' : microExpenses})
    return render(request, 'student_spend/expenses.html', {'mostRecentData' : mostRecentData, 'allData' : allData},)

@login_required 
def bill_splitting(request):
    profile = request.user.userprofile
    if request.method == 'POST':
        action = request.POST.get("action")
        if action == "add_group":
            userCreatedGroupName = request.POST.get('userCreatedGroupName')
            moneySpent = Decimal(request.POST.get('moneySpent'))
            if (MemberOfGroup.objects.filter(user=profile, group_name_for_user = userCreatedGroupName).exists()):
                messages.error(request, "Group of same name already exists.")
            else:
                groupmembers = request.POST.getlist('members')
                moneyPerUser=moneySpent/Decimal(len(groupmembers)+1)

                #Check all fields are valid before making group
                for memberUsername in groupmembers:# is there a sepreate user id or id it onley the username
                    if (not(User.objects.filter(username=memberUsername).exists())):
                        messages.error(request, "User, " + memberUsername +", does not exist. Could not make group")
                else:
                    new_group=Group.objects.create(name=userCreatedGroupName, money_per_user=moneyPerUser, total_money=moneySpent)
                    MemberOfGroup.objects.create(user=profile, group=new_group,group_name_for_user=userCreatedGroupName, groupAdmin=True)
                    for memberUsername in groupmembers:
                        userMember = User.objects.filter(username=memberUsername)
                        userMemberProfile = UserProfile.objects.get(user=userMember.get())
                        addMember(userMemberProfile, new_group, userCreatedGroupName)
        
        elif action == "add_member": #we need to ad a way to get the user ID from the username dodnt know if it works
            memberUsername = request.POST.get('membersUsername')
            groupName = request.POST.get('groupName')
            if (not(MemberOfGroup.objects.get(user=profile, group_name_for_user=groupName).groupAdmin)):
                messages.error(request, "You are not an admin of " + groupName +". Only the creator of the group can add members")
            elif (not(User.objects.filter(username=memberUsername)).exists()):
                messages.error(request, "User, " + memberUsername +", does not exist. Could not add to group")

            elif (not(MemberOfGroup.objects.filter(user=profile, group_name_for_user=groupName)).exists()):
                messages.error(request, "You are not a member of a group called " + groupName)

            else:
                userMember = User.objects.filter(username=memberUsername)
                userMemberProfile = UserProfile.objects.get(user=userMember.get())
                memberGroup = MemberOfGroup.objects.get(user=profile, group_name_for_user=groupName).group
                if (MemberOfGroup.objects.filter(user=userMemberProfile, group=memberGroup).exists()):
                    messages.error(request, memberUsername + " is already in " + groupName +". Could npt add to group")
                else:
                    addMember(userMemberProfile, memberGroup, groupName)
                    memberGroup.money_per_user = memberGroup.total_money / Decimal(memberGroup.numberOfUsers)
                    memberGroup.save()

        elif action == "remove_member":
            memberUsername = request.POST.get('membersUsername')
            groupName = request.POST.get('groupName')
            if (not(MemberOfGroup.objects.get(user=profile, group_name_for_user=groupName).groupAdmin)):
                messages.error(request, "You are not an admin of " + groupName +". Only the creator of the group can remove members")
            elif (not(User.objects.filter(username=memberUsername)).exists()):
                messages.error(request, "User, " + memberUsername +", does not exist. Could not remove from group")

            elif (not(MemberOfGroup.objects.filter(user=profile, group_name_for_user=groupName)).exists()):
                messages.error(request, "You are not a member of a group called " + groupName )

            else:
                userMember = User.objects.filter(username=memberUsername)
                userMemberProfile = UserProfile.objects.get(user=userMember.get())
                memberGroup = MemberOfGroup.objects.get(user=profile, group_name_for_user=groupName).group
                if (not(MemberOfGroup.objects.filter(user=userMemberProfile, group=memberGroup).exists())):
                    messages.error(request, memberUsername + " is not in " + groupName +". Could not remove for group")
                else:
                    MemberOfGroup.objects.filter(user=userMemberProfile, group=memberGroup).delete()
                    memberGroup.numberOfUsers -= 1
                    memberGroup.money_per_user = memberGroup.total_money / Decimal(memberGroup.numberOfUsers)
                    memberGroup.save()

        elif action == "delete_group":
            groupName = request.POST.get('groupName')
            if (not(MemberOfGroup.objects.get(user=profile, group_name_for_user=groupName).groupAdmin)):
                messages.error(request, "You are not an admin of " + groupName +". Only the creator of the group can remove members")
            elif (not(MemberOfGroup.objects.filter(user=profile, group_name_for_user=groupName)).exists()):
                messages.error(request, "You are not a member of a group called " + groupName)
            else:
                group = MemberOfGroup.objects.get(user=profile, group_name_for_user=groupName).group
                group.delete()

        elif action == "add_transaction": 
            nameForGroup = request.POST.get('groupName')
            groupTransaction = Decimal(request.POST.get('transaction')) 

            if (groupTransaction > 0):
                memberOfGroup= MemberOfGroup.objects.get(user=profile, group_name_for_user = nameForGroup)
                moneyForT= Group.objects.get(id=memberOfGroup.group_id)
                if (moneyForT.money_per_user <= groupTransaction):
                    memberOfGroup.paid_off = True
                memberOfGroup.money_spent = memberOfGroup.money_spent + groupTransaction
                memberOfGroup.lastPayment = datetime.now()
                memberOfGroup.save()
            else:
                messages.error(request, "Please enter a transaction")

    groups = MemberOfGroup.objects.filter(user=profile).order_by('group_name_for_user')
    memberG = MemberOfGroup.objects.filter(user=profile, paid_off = False).order_by('group_name_for_user').values().reverse()
    memberG = memberG[:5]
    mostRecentData = []
    for memberGroup in memberG:
        group = Group.objects.get(id=memberGroup['group_id'])
        otherMembers = MemberOfGroup.objects.filter(group_id=memberGroup['group_id']).exclude(user=profile)
        mostRecentData.append({'name' : memberGroup['group_name_for_user'], 'money_spent' : memberGroup['money_spent'], 'money_per_user' : group.money_per_user, 'other_members' : otherMembers,})


    return render(request, 'student_spend/bill-splitting.html', {'mostRecentData' : mostRecentData, 'groups' : groups,},)

def addMember(userProfile, group, groupName):
    alsoMemberIn=MemberOfGroup.objects.filter(user=userProfile, paid_off = False ).order_by('lastPayment').values().reverse() 
    membersNameForGroup=groupName
    if alsoMemberIn and (alsoMemberIn['group_name_for_user'] == groupName):
        if (membersNameForGroup[-1].isDigit()):
            membersNameForGroup=checkNumber(membersNameForGroup, -1)
        else:
            membersNameForGroup=membersNameForGroup+"1"
    MemberOfGroup.objects.create(user=userProfile,group=group,group_name_for_user=membersNameForGroup)
    group.numberOfUsers = group.numberOfUsers + 1
    group.save()

def checkNumber(string, numberChecker):
    if (string[numberChecker-1].isdigit() and int(string[numberChecker]) == 9):
        string = checkNumber(string, numberChecker-1)
    elif (int(string[numberChecker]) == 9):
        string = string[:numberChecker]+"10"+string[numberChecker:]
    else:
        string = string[:numberChecker]+str(int(string[numberChecker])+1)+string[numberChecker+1:]
    return string

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
            return redirect(reverse('student_spend:dashboard'))
        except:
            return HttpResponse("Invalid input supplied.")
    return render(request, 'student_spend/add-money.html')

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
                return redirect(reverse('student_spend:remove_money'))
            else:
                profile.money -= total
                profile.save()
                return redirect(reverse('student_spend:dashboard'))
        except:
            messages.error(request, "Invalid input supplied.")
    return render(request, 'student_spend/remove-money.html')

def view_all_expenses(request):
    profile = request.user.userprofile
    categories = ExpenseCategory.objects.filter(user=profile).order_by('lastAddedTo').values().reverse()
    allData = []
    for category in categories:
        microExpenses = Expense.objects.filter(user=profile, category_id = category['id']).order_by('date').values().reverse()
        allData.append({'category' : category, 'expenses' : microExpenses})
    return render(request, 'student_spend/view-all-expenses.html', {'allData' : allData},)