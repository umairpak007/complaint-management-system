from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('engineer', 'Engineer'),
        ('operations', 'Operations'),  # NEW
        ('analytics', 'Analytics'),     # NEW
        ('manager', 'Manager'),         # NEW
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='engineer')
    contact_no = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.role})"
