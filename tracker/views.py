from django.shortcuts import render

import uuid
import hashlib
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q, Count, Sum
from django.utils import timezone

from .models import Employee, PasswordResetToken, AdminUser
from .forms import (
    ManagerRegisterForm, ManagerLoginForm,
    ForgotPasswordForm, ResetPasswordForm, EmployeeForm,
    AdminLoginForm, AdminRegisterForm
)

# ── Secret key to create first admin (change this!) ───────────────────────────
ADMIN_SECRET_KEY = "emptrack@admin2024"


# ─── Helpers ──────────────────────────────────────────────────────────────────

def hash_password(raw):
    return hashlib.sha256(raw.encode()).hexdigest()


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('admin_logged_in'):
            messages.error(request, 'Please login to access the admin panel.')
            return redirect('admin_login')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


# ─── Manager Auth ─────────────────────────────────────────────────────────────

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = ManagerRegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f'Welcome, {user.username}! Account created.')
        return redirect('dashboard')
    return render(request, 'tracker/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = ManagerLoginForm(data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, f'Welcome back, {user.username}!')
        return redirect('dashboard')
    elif request.method == 'POST':
        messages.error(request, 'Invalid username or password.')
    return render(request, 'tracker/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


def forgot_password_view(request):
    form = ForgotPasswordForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email']
        try:
            user = User.objects.get(email=email)
            token = str(uuid.uuid4()).replace('-', '')
            PasswordResetToken.objects.create(user=user, token=token)
            reset_url = request.build_absolute_uri(f'/reset-password/{token}/')
            messages.success(request, f'Reset link (dev mode): {reset_url}')
        except User.DoesNotExist:
            messages.error(request, 'No account found with that email address.')
    return render(request, 'tracker/forgot_password.html', {'form': form})


def reset_password_view(request, token):
    reset_obj = get_object_or_404(PasswordResetToken, token=token, used=False)
    form = ResetPasswordForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = reset_obj.user
        user.set_password(form.cleaned_data['password1'])
        user.save()
        reset_obj.used = True
        reset_obj.save()
        messages.success(request, 'Password reset successful! Please log in.')
        return redirect('login')
    return render(request, 'tracker/reset_password.html', {'form': form, 'token': token})


# ─── Manager Dashboard ────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    search_query = request.GET.get('q', '')
    employees = Employee.objects.filter(manager=request.user)
    if search_query:
        employees = employees.filter(
            Q(name__icontains=search_query) |
            Q(role__icontains=search_query) |
            Q(previous_project__icontains=search_query)
        )
    return render(request, 'tracker/dashboard.html', {
        'employees': employees,
        'search_query': search_query,
        'total_count': Employee.objects.filter(manager=request.user).count(),
    })


@login_required
def add_employee(request):
    form = EmployeeForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        employee = form.save(commit=False)
        employee.manager = request.user
        employee.save()
        messages.success(request, f'{employee.name} has been added successfully!')
        return redirect('dashboard')
    return render(request, 'tracker/employee_form.html', {
        'form': form, 'title': 'Add New Employee', 'action': 'Add'
    })


@login_required
def edit_employee(request, pk):
    employee = get_object_or_404(Employee, pk=pk, manager=request.user)
    form = EmployeeForm(request.POST or None, request.FILES or None, instance=employee)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'{employee.name} has been updated.')
        return redirect('employee_detail', pk=pk)
    return render(request, 'tracker/employee_form.html', {
        'form': form, 'title': 'Edit Employee', 'action': 'Update', 'employee': employee
    })


@login_required
def employee_detail(request, pk):
    employee = get_object_or_404(Employee, pk=pk, manager=request.user)
    return render(request, 'tracker/employee_detail.html', {'employee': employee})


@login_required
def delete_employee(request, pk):
    employee = get_object_or_404(Employee, pk=pk, manager=request.user)
    if request.method == 'POST':
        name = employee.name
        employee.delete()
        messages.success(request, f'{name} has been removed.')
        return redirect('dashboard')
    return render(request, 'tracker/confirm_delete.html', {'employee': employee})


# ─── Custom Admin Panel ───────────────────────────────────────────────────────

def admin_register_view(request):
    if request.session.get('admin_logged_in'):
        return redirect('admin_dashboard')

    form = AdminRegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        data = form.cleaned_data

        if data['secret_key'] != ADMIN_SECRET_KEY:
            messages.error(request, 'Invalid secret key.')
            return render(request, 'admin/admin_register.html', {'form': form})

        if AdminUser.objects.filter(username=data['username']).exists():
            messages.error(request, 'Username already taken.')
            return render(request, 'admin/admin_register.html', {'form': form})

        if AdminUser.objects.filter(email=data['email']).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'admin/admin_register.html', {'form': form})

        AdminUser.objects.create(
            username=data['username'],
            email=data['email'],
            password=hash_password(data['password'])
        )
        messages.success(request, 'Admin account created! Please login.')
        return redirect('admin_login')

    return render(request, 'admin/admin_register.html', {'form': form})


def admin_login_view(request):
    if request.session.get('admin_logged_in'):
        return redirect('admin_dashboard')

    form = AdminLoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        try:
            admin = AdminUser.objects.get(
                username=username,
                password=hash_password(password)
            )
            request.session['admin_logged_in'] = True
            request.session['admin_username'] = admin.username
            request.session['admin_id'] = admin.id
            messages.success(request, f'Welcome back, {admin.username}!')
            return redirect('admin_dashboard')
        except AdminUser.DoesNotExist:
            messages.error(request, 'Invalid admin credentials.')

    return render(request, 'admin/admin_login.html', {'form': form})


def admin_logout_view(request):
    request.session.flush()
    messages.info(request, 'Admin logged out.')
    return redirect('admin_login')


@admin_required
def admin_dashboard(request):
    total_managers  = User.objects.count()
    total_employees = Employee.objects.count()
    total_admins    = AdminUser.objects.count()

    managers = User.objects.annotate(emp_count=Count('employees')).order_by('-date_joined')

    recent_employees = Employee.objects.select_related('manager').order_by('-created_at')[:8]

    return render(request, 'admin/admin_dashboard.html', {
        'total_managers':  total_managers,
        'total_employees': total_employees,
        'total_admins':    total_admins,
        'managers':        managers,
        'recent_employees': recent_employees,
        'admin_username':  request.session.get('admin_username'),
    })


@admin_required
def admin_managers_list(request):
    search = request.GET.get('q', '')
    managers = User.objects.annotate(emp_count=Count('employees')).order_by('-date_joined')
    if search:
        managers = managers.filter(
            Q(username__icontains=search) | Q(email__icontains=search)
        )
    return render(request, 'admin/admin_managers.html', {
        'managers': managers,
        'search': search,
        'admin_username': request.session.get('admin_username'),
    })


@admin_required
def admin_manager_detail(request, pk):
    manager = get_object_or_404(User, pk=pk)
    employees = Employee.objects.filter(manager=manager)
    return render(request, 'admin/admin_managers.html', {
        'manager': manager,
        'employees': employees,
        'admin_username': request.session.get('admin_username'),
    })


@admin_required
def admin_delete_manager(request, pk):
    manager = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        name = manager.username
        manager.delete()
        messages.success(request, f'Manager "{name}" and all their employees deleted.')
        return redirect('admin_managers_list')
    return render(request, 'admin/admin_confirm_delete.html', {
        'object_type': 'Manager',
        'object_name': manager.username,
        'cancel_url': 'admin_managers_list',
        'admin_username': request.session.get('admin_username'),
    })


@admin_required
def admin_employees_list(request):
    search = request.GET.get('q', '')
    employees = Employee.objects.select_related('manager').order_by('-created_at')
    if search:
        employees = employees.filter(
            Q(name__icontains=search) |
            Q(role__icontains=search) |
            Q(previous_project__icontains=search) |
            Q(manager__username__icontains=search)
        )
    return render(request, 'admin/admin_employees.html', {
        'employees': employees,
        'search': search,
        'admin_username': request.session.get('admin_username'),
    })


@admin_required
def admin_employee_detail(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    return render(request, 'admin/admin_employee_detail.html', {
        'employee': employee,
        'admin_username': request.session.get('admin_username'),
    })


@admin_required
def admin_delete_employee(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        name = employee.name
        employee.delete()
        messages.success(request, f'Employee "{name}" deleted.')
        return redirect('admin_employees_list')
    return render(request, 'admin/admin_confirm_delete.html', {
        'object_type': 'Employee',
        'object_name': employee.name,
        'cancel_url': 'admin_employees_list',
        'admin_username': request.session.get('admin_username'),
    })


@admin_required
def admin_admins_list(request):
    admins = AdminUser.objects.all().order_by('-created_at')
    return render(request, 'admin/admin_admins.html', {
        'admins': admins,
        'admin_username': request.session.get('admin_username'),
    })


@admin_required
def admin_delete_admin(request, pk):
    current_id = request.session.get('admin_id')
    admin_obj = get_object_or_404(AdminUser, pk=pk)
    if str(admin_obj.id) == str(current_id):
        messages.error(request, "You can't delete your own admin account.")
        return redirect('admin_admins_list')
    if request.method == 'POST':
        name = admin_obj.username
        admin_obj.delete()
        messages.success(request, f'Admin "{name}" deleted.')
        return redirect('admin_admins_list')
    return render(request, 'admin/admin_confirm_delete.html', {
        'object_type': 'Admin',
        'object_name': admin_obj.username,
        'cancel_url': 'admin_admins_list',
        'admin_username': request.session.get('admin_username'),
    })

from .forms import EmployeeForm

def employee_self_form(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')   # after employee submits
    else:
        form = EmployeeForm()

    return render(request, 'tracker/employee_self_form.html', {'form': form})

# Create your views here.
