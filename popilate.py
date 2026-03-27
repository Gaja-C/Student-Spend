import os
import django
import random
from decimal import Decimal
from datetime import date, timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_spend_project.settings')
django.setup()

from django.contrib.auth.models import User
from student_spend.models import (
    UserProfile,
    ExpenseCategory,
    Expense,
    Group,
    MemberOfGroup,
    Goal
)

def create_user(username, money):
    user, created = User.objects.get_or_create(username=username)
    if created:
        user.set_password("123456")
        user.save()

    profile, _ = UserProfile.objects.get_or_create(
        user=user,
        defaults={"money": Decimal(money)}
    )
    return profile


def create_categories(user):
    categories = ["Food", "Doing Evil", "Entertainment", "Pets", "Bills"]
    created = []
    for cat in categories:
        c, o = ExpenseCategory.objects.get_or_create(user=user,name=cat,defaults={"lastAddedTo": timezone.now()})
        created.append(c)

    return created

def create_expenses(user, categories):
    for i in range(5):
        cat = random.choice(categories)
        amount = Decimal(random.randint(5, 50))

        Expense.objects.create(user=user,category=cat,amount=amount,date=timezone.now().date())

        cat.lastAddedTo = timezone.now()
        cat.save()
        user.money -= amount
        user.save()

def create_group(name, members, total_money):
    group = Group.objects.create(name=name,total_money=Decimal(total_money),numberOfUsers=len(members))
    money_per_user = (group.total_money / Decimal(len(members))).quantize(Decimal("0.01"))
    group.money_per_user = money_per_user
    group.save()

    for i, member in enumerate(members):
        MemberOfGroup.objects.create(user=member,group=group,group_name_for_user=name,groupAdmin=(i == 0),money_spent=Decimal(random.randint(0, int(money_per_user))),paid_off=False )

    return group

def create_goals(user):
    goals_data = [("World Domination", 1200),("Holiday", 600),("Emergency Fund", 1000),]

    for name, budget in goals_data:
        current = Decimal(random.randint(0, int(budget / 2)))
        Goal.objects.create(user=user,name=name,budget=Decimal(budget),current_amount=current,date=date.today() + timedelta(days=random.randint(30, 180)))

def populate():
    print("start")
    cookieMonster = create_user("CookieMonster", 500)
    bob = create_user("bob", 400)
    drWho = create_user("DrWho", 300)
    brain = create_user("Brain", 600)

    users = [cookieMonster, bob, drWho, brain]

    for user in users:
        cats = create_categories(user)
        create_expenses(user, cats)

    create_group("Flat Bills", [cookieMonster, bob, drWho], 150)
    create_group("Night Out", [cookieMonster, brain], 80)
    create_group("Cheese", [bob, drWho, brain], 210)

    for user in users:
        create_goals(user)
    
    print("there should be data now yeyyyyyyyyyyyyyyyyyyyyyyyyyyyy")

if __name__ == "__main__":
    populate()