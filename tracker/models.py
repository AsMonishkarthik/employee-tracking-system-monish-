from django.db import models
from django.contrib.auth.models import User


class Employee(models.Model):
    manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='employees')
    name            = models.CharField(max_length=200)
    address         = models.TextField()
    role            = models.CharField(max_length=200)
    current_salary  = models.DecimalField(max_digits=12, decimal_places=2)
    previous_project            = models.CharField(max_length=300)
    previous_project_experience = models.TextField()
    passport_photo  = models.ImageField(upload_to='passport_photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    email = models.EmailField(blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.role})"


class PasswordResetToken(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE)
    token      = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    used       = models.BooleanField(default=False)

    def __str__(self):
        return f"Reset token for {self.user.username}"


class AdminUser(models.Model):
    username    = models.CharField(max_length=100, unique=True)
    password    = models.CharField(max_length=255)
    email       = models.EmailField(unique=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

# Create your models here.
