from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.


class Company(models.Model):
    company_name = models.CharField(max_length=20)
    address = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f'{self.company_name}'


class MyUser(AbstractUser):
    """login by email, so we remove username filed"""
    username = None
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True)
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


class Office(models.Model):
    office_name = models.CharField(max_length=20)
    address = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    region = models.CharField(max_length=50)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True)
    employee = models.ForeignKey(MyUser, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f'{self.office_name}'


class Vehicle(models.Model):
    """Vehicle create, year of manufacture - you can choose between from 1984 to today"""
    year = [(r, r) for r in range(1984, timezone.now().year + 1)]
    today = timezone.now().year
    licence_plate = models.CharField(max_length=20)
    name = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year_of_manufacture = models.IntegerField(('year'), choices=year, default=today)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True)
    office = models.ForeignKey(Office, on_delete=models.CASCADE, blank=True, null=True)
    driver = models.ForeignKey(MyUser, on_delete=models.CASCADE, blank=True, null=True)
