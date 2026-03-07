from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Employee, AdminUser
import hashlib


class ManagerRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-input', 'placeholder': 'Email address'
    }))
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-input', 'placeholder': 'Username'
    }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-input', 'placeholder': 'Password'
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-input', 'placeholder': 'Confirm Password'
    }))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class ManagerLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-input', 'placeholder': 'Username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-input', 'placeholder': 'Password'
    }))


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-input', 'placeholder': 'Enter your registered email'
    }))


class ResetPasswordForm(forms.Form):
    password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'New password'})
    )
    password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Confirm new password'})
    )

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        exclude = ['manager', 'created_at', 'updated_at']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Full name'}),
            'address': forms.Textarea(attrs={'class': 'form-input', 'placeholder': 'Full address', 'rows': 3}),
            'role': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Frontend Developer'}),
            'current_salary': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '0.00'}),
            'previous_project': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Previous project name'}),
            'previous_project_experience': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Describe experience, achievements, and skills gained...',
                'rows': 4
            }),
            'passport_photo': forms.FileInput(attrs={'class': 'form-file', 'accept': 'image/*'}),
        }


# ── Custom Admin Forms ────────────────────────────────────────────────────────

class AdminLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-input', 'placeholder': 'Admin username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-input', 'placeholder': 'Admin password'
    }))


class AdminRegisterForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-input', 'placeholder': 'Admin username'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-input', 'placeholder': 'Admin email'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-input', 'placeholder': 'Password'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-input', 'placeholder': 'Confirm password'
    }))
    secret_key = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-input', 'placeholder': 'Secret setup key'
    }), help_text="Required to create admin accounts")

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('confirm_password')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data