from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to='profile_images', blank=True)
    money = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.user.username

class ExpenseCategory(models.Model):
    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name

class Expense(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10,decimal_places=2, null=True, blank=True)
    date = models.DateField()

    def __str__(self):
        return self.name

class Goal(models.Model):
    user =models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    budget = models.DecimalField(max_digits=10,decimal_places=2, null=True, blank=True)
    current_amount = models.DecimalField(max_digits=10,decimal_places=2, null=True, blank=True)
    date = models.DateField()

    def __str__(self):
        return self.name

class MemberOfGroup(models.Model): # if the name given by one person already exists for another member of the group the name should be able to get a different identifier for the user 
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    group = models.ForeignKey("Group", on_delete=models.CASCADE)
    group_name_for_user = models.CharField(max_length=128) 

    class Meta:
        constraints = [
            models.UniqueConstraint(  # this part works with the ID so a person is not twice added to the group
                fields=["user", "group"], name="unique_person_group"
            ),
            models.UniqueConstraint( # different name for a user but not the same name a user already has
                fields=["user", "group_name_for_user"], name="no_two_same_names"
            )
        ]

class Group(models.Model):
    name = models.CharField(max_length=128, unique=True)   #name first given
    money_spent = models.DecimalField(max_digits=10,decimal_places=2, null=True, blank=True)
    members = models.ManyToManyField(UserProfile, through="MemberOfGroup")

    def __str__(self):
        return self.name