from django.test import TestCase, Client
import os
from student_spend.models import (
    UserProfile, ExpenseCategory, Expense,
    Goal, Group, MemberOfGroup
)
from django.urls import reverse
from decimal import Decimal
from datetime import date
from django.contrib.auth.models import User

FAILURE_HEADER = f"{os.linesep}{os.linesep}{os.linesep}================{os.linesep}TwD TEST FAILURE =({os.linesep}================{os.linesep}"
FAILURE_FOOTER = f"{os.linesep}"

class BasePageTest(TestCase): #dose stuff openen 

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="user", password="123456")
        self.profile = UserProfile.objects.create(user=self.user)
        self.client.login(username="user", password="123456")
    
    def test_index_view(self): #index page opens 
        response = self.client.get(reverse('student_spend:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_spend/index.html')

    def test_registration_page(self): # registration opens
        response = self.client.get(reverse('student_spend:registration'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_spend/registration.html')

    def test_registration(self): # registration lets user register
        response = self.client.post(
            reverse('student_spend:registration'),
            {
                "username": "newuser",
                "password": "123456",
                "money": "0"
            }   
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_login_page(self): # login opens
        response = self.client.get(reverse('student_spend:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_spend/login.html')
    
    def test_login_right_password(self): 
        response = self.client.post(
            reverse('student_spend:login'),
            {
                "username": "user",
                "password": "123456"
            }
        )
        self.assertEqual(response.status_code, 302)  # user gets redirected (they are able to login)
        #self.assertNotContains(response, "Invalid login details")

    def test_login_wrong_password(self): 
        response = self.client.post(
            reverse('student_spend:login'),
            {
                "username": "testuser",
                "password": "wrong"
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid login details")

    def test_logout(self): # logout works
        self.client.login(username="user", password="123456")
        response = self.client.get(reverse('student_spend:logout'))
        self.assertEqual(response.status_code, 302)

class BaseMoneyTests(TestCase):

    def setUp(self): 
        self.user1 = User.objects.create_user(username="testuser1",email="test@mail.org", password="123456")
        self.profile1 = UserProfile.objects.create(user=self.user1, money=100)
     
    def test_user_profile_creation(self):
        self.assertEqual(self.profile1.user.username, "testuser1")
        self.assertEqual(self.profile1.money, 100)

    def test_money_2decemals(self):
        with self.assertRaises(Exception):
            self.profile1 = UserProfile.objects.create(user=self.user1, money=100.777)

class ExpenseTests(TestCase): 

    def setUp(self):
        self.user = User.objects.create_user(username="user", password="123456")
        self.profile = UserProfile.objects.create(user=self.user)
        self.client.login(username="user", password="123456")

    def test_create_category(self):  # dose the database work
        ExpenseCategory.objects.create(user=self.profile, name="Food")
        self.assertTrue(
            ExpenseCategory.objects.filter(name="Food").exists()
        )

    def test_unique_category(self): # a user souldnt have the same categrory multible times
        ExpenseCategory.objects.create(user=self.profile, name="Food")
        with self.assertRaises(Exception):
            ExpenseCategory.objects.create(user=self.profile, name="Food")

    def test_add_expense(self): # dose the database work
        category = ExpenseCategory.objects.create(user=self.profile, name="Food")

        Expense.objects.create(
            user=self.profile,
            name="Pasta",
            category=category,
            amount=10,
            date=date.today()
        )

        self.assertEqual(Expense.objects.count(), 1)

    def test_expense_view_add(self): #dose view work
        ExpenseCategory.objects.create(user=self.profile, name="Food")

        self.client.post(reverse('student_spend:expenses'), {
            "action": "add_expense",
            "expenseName": "Pasta",
            "categoryName": "Food",
            "amount": "10",
            "date": "2026-01-01"
        })

        self.assertTrue(Expense.objects.filter(name="Pasta").exists())

class GroupTests(TestCase):

    def setUp(self):
        self.client = Client()

        # Create users
        self.user1 = User.objects.create_user(username="user1", password="123456")
        self.user2 = User.objects.create_user(username="user2", password="123456")
        self.user3 = User.objects.create_user(username="user3", password="123456")

        # Profiles
        self.profile1 = UserProfile.objects.create(user=self.user1)
        self.profile2 = UserProfile.objects.create(user=self.user2)
        self.profile3 = UserProfile.objects.create(user=self.user3)

        self.client.login(username="user1", password="123456")

    def test_create_group_and_admin_member(self): #test if database works at all 
        group = Group.objects.create(name="Trip", total_money=Decimal("90")) 
        member = MemberOfGroup.objects.create(user=self.profile1,group=group,group_name_for_user="Trip",groupAdmin=True)

        self.assertEqual(group.name, "Trip")
        self.assertTrue(member.groupAdmin)

    def test_unique_user_group_constraint(self): #a user sould not be in  a group more then once 
        group = Group.objects.create(name="Trip")
        MemberOfGroup.objects.create(user=self.profile1,group=group,group_name_for_user="Trip")
        
        with self.assertRaises(Exception):
            MemberOfGroup.objects.create(user=self.profile1,group=group,group_name_for_user="Trip2")

    def test_unique_group_name_per_user(self): #a user sould not be displyed the same group multiple times
        group1 = Group.objects.create(name="Trip1")
        group2 = Group.objects.create(name="Trip2")

        MemberOfGroup.objects.create(user=self.profile1,group=group1,group_name_for_user="SameName") 

        with self.assertRaises(Exception): #a user should onley be displayed groups whit unice names 
            MemberOfGroup.objects.create(user=self.profile1,group=group2, group_name_for_user="SameName")

    def test_add_group(self): #wenn group is created dose it get the number of members right
        response = self.client.post(reverse('student_spend:bill_splitting'), {
            "action": "add_group",
            "userCreatedGroupName": "Holiday",
            "moneySpent": "100",
            "members": ["user2", "user3"]
        })

        self.assertEqual(response.status_code, 200) # is the page loading
        self.assertTrue(Group.objects.filter(name="Holiday").exists())

        group = Group.objects.get(name="Holiday")
        self.assertEqual(group.numberOfUsers, 3)

    def test_add_group_invalid_user(self): #dose not create groups wiht users that dont exist
        response = self.client.post(reverse('student_spend:bill_splitting'), {
            "action": "add_group",
            "userCreatedGroupName": "BadGroup",
            "moneySpent": "100",
            "members": ["userDoseNotExist"]
        })

        
        self.assertFalse(Group.objects.filter(name="BadGroup").exists())

    def test_add_member_by_admin(self): #admin can add members
        group = Group.objects.create(name="Trip", total_money=100)
        MemberOfGroup.objects.create(user=self.profile1,group=group,group_name_for_user="Trip",groupAdmin=True)

        response = self.client.post(reverse('student_spend:bill_splitting'), {
            "action": "add_member",
            "membersUsername": "user2",
            "groupName": "Trip"
        })

        self.assertEqual(response.status_code, 200) #is page loading
        self.assertTrue(MemberOfGroup.objects.filter(user=self.profile2, group=group).exists())

    def test_add_member_not_admin(self): #users that are not admin of a group souhld not be able to add members to said group
        group = Group.objects.create(name="Trip")
        MemberOfGroup.objects.create(user=self.profile1,group=group,group_name_for_user="Trip",groupAdmin=False) #no admin for user1

        response = self.client.post(reverse('student_spend:bill_splitting'), {
            "action": "add_member",
            "membersUsername": "user2",
            "groupName": "Trip"
        })

        self.assertFalse(MemberOfGroup.objects.filter(user=self.profile2, group=group).exists())

    def test_remove_member(self): #admin can remove members from group
        group = Group.objects.create(name="Trip", total_money=100)
        MemberOfGroup.objects.create(user=self.profile1,group=group,group_name_for_user="Trip",groupAdmin=True)
        MemberOfGroup.objects.create(user=self.profile2,group=group,group_name_for_user="Trip2")

        response = self.client.post(reverse('student_spend:bill_splitting'), {
            "action": "remove_member",
            "membersUsername": "user2",
            "groupName": "Trip"
        })

        self.assertFalse(
            MemberOfGroup.objects.filter(user=self.profile2, group=group).exists()
        )

    def test_money_per_user_rounding(self): # test money rounding
        response = self.client.post(
        reverse('student_spend:bill_splitting'),
        {
            "action": "add_group",
            "userCreatedGroupName": "RoundingGroup",
            "moneySpent": "100",
            "members": ["user2", "user3"]  
        }
        )
        group = Group.objects.get(name="RoundingGroup")
        #(100 / 3 = 33.33)
        self.assertEqual(group.money_per_user, Decimal("33.33"))

    def test_delete_group_by_admin(self): # admin can delete group
        group = Group.objects.create(name="Trip")
        MemberOfGroup.objects.create(user=self.profile1,group=group,group_name_for_user="Trip",groupAdmin=True)

        response = self.client.post(reverse('student_spend:bill_splitting'), {
            "action": "delete_group",
            "groupName": "Trip"
        })

        self.assertFalse(Group.objects.filter(name="Trip").exists())

    def test_delete_group_not_admin(self): #users that are not admin of a group souhld not be able to remove members of said group
        group = Group.objects.create(name="Trip")
        MemberOfGroup.objects.create(user=self.profile1,group=group,group_name_for_user="Trip",groupAdmin=False)

        response = self.client.post(reverse('student_spend:bill_splitting'), {
            "action": "delete_group",
            "groupName": "Trip"
        })

        self.assertTrue(Group.objects.filter(name="Trip").exists())

    def test_add_transaction_marks_paid(self): # users cen pay of the money
        group = Group.objects.create(name="Trip",total_money=100,money_per_user=Decimal("50"))
        member = MemberOfGroup.objects.create(user=self.profile1,group=group,group_name_for_user="Trip")

        response = self.client.post(reverse('student_spend:bill_splitting'), {
            "action": "add_transaction",
            "groupName": "Trip",
            "transaction": "50"
        })

        member.refresh_from_db()
        self.assertTrue(member.paid_off)

    def test_add_transaction_more_then_once_money(self):  # users cen pay of the money repiededly
        group = Group.objects.create(name="Trip",total_money=100,money_per_user=Decimal("50"))
        member = MemberOfGroup.objects.create(user=self.profile1,group=group,group_name_for_user="Trip")

        self.client.post(reverse('student_spend:bill_splitting'), {
            "action": "add_transaction",
            "groupName": "Trip",
            "transaction": "20"
        })

        self.client.post(reverse('student_spend:bill_splitting'), {
            "action": "add_transaction",
            "groupName": "Trip",
            "transaction": "10"
        })

        member.refresh_from_db()
        self.assertEqual(member.money_spent, Decimal("30"))

    def test_admin_reassignment_and_group_deletion(self): 

    #wenn the admin removes themself one of the other members will become admin 
    #wenn all users are removed from a group the group gets deleted
        self.client.post(
            reverse('student_spend:bill_splitting'),
            {
                "action": "add_group",
                "userCreatedGroupName": "UserRemoverG",
                "moneySpent": "90",
                "members": ["user2", "user3"]
            }
        )

        group = Group.objects.get(name="UserRemoverG")

        response = self.client.post( #remove admin 
            reverse('student_spend:bill_splitting'),
            {
                "action": "remove_member",
                "membersUsername": "user1",
                "groupName": "UserRemoverG"
            }
        )

        members = MemberOfGroup.objects.filter(group=group)
        self.assertTrue(Group.objects.filter(name="UserRemoverG").exists()) # group still here 
        new_admin_exists = members.filter(groupAdmin=True).exists() 
        self.assertTrue(new_admin_exists) #new admin was assigned?

        # remove rest of members
        new_admin = members.filter(groupAdmin=True).first().user.user
        self.client.login(username=new_admin.username, password="123456")

        self.client.post(
            reverse('student_spend:bill_splitting'),
            {
                "action": "remove_member",
                "membersUsername": "user3",
                "groupName": "UserRemoverG"
            }
        )

        self.client.post(
            reverse('student_spend:bill_splitting'),
            {
                "action": "remove_member",
                "membersUsername": "user2",
                "groupName": "UserRemoverG"
            }
        )
        self.assertFalse(Group.objects.filter(name="UserRemoverG").exists()) #group should be deleted

class GoalTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="user", password="123456")
        self.profile = UserProfile.objects.create(user=self.user)
        self.client.login(username="user", password="123456")

    def test_add_goal(self): # database works call from view
        self.client.post(reverse('student_spend:budget'), {
            "action": "add_goal",
            "goalName": "money",
            "amount": "100",
            "date": "2026-01-01"
        })

        self.assertTrue(Goal.objects.filter(name="money").exists())

    def test_remove_goal(self): #removing goal works
        Goal.objects.create(
            user=self.profile,
            name="money",
            budget=100,
            current_amount=0,
            date="2026-01-01"
        )

        self.client.post(reverse('student_spend:budget'), {
            "action": "remove_goal",
            "goalName": "money",
            "date": "2026-01-01"
        })

        self.assertFalse(Goal.objects.filter(name="money").exists())

    def test_getting_closer_to_goal(self): #dose adding saved money work
        goal = Goal.objects.create(
            user=self.profile,
            name="money",
            budget=100,
            current_amount=10,
            date="2026-01-01"
        )

        self.client.post(reverse('student_spend:budget'), {
            "action": "edit_goal",
            "goalName": "money",
            "amount": "20"
        })

        goal.refresh_from_db()
        self.assertEqual(goal.current_amount, 30)