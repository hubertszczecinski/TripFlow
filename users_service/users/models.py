from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    
    class Role(models.TextChoices):
        EMPLOYEE = "EMPLOYEE"
        FINANCE = "FINANCE"
        HR = "HR"
        ADMIN = "ADMIN"

    class Position(models.TextChoices):
        JUNIOR = "JUNIOR"
        MID = "MID"
        SENIOR = "SENIOR"
        DIRECTOR = "DIRECTOR"
        INTERN = "INTERN"

    role = models.CharField(max_length=30, default=Role.EMPLOYEE)
    position = models.CharField(max_length=30, choices=Position.choices, default=Position.INTERN)

    department = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    is_blocked = models.BooleanField(default=False)
    assigned_car_id = models.IntegerField(null=True, blank=True)