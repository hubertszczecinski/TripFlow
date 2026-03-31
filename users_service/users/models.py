from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    
    class Role(models.TextChoices):
        EMPLOYEE = "EMPLOYEE"
        FINANCE = "FINANCE"
        HR = "HR"
        ADMIN = "ADMIN"

    role = models.CharField(max_length=30, default=Role.EMPLOYEE)
    is_blocked = models.BooleanField(default=False)