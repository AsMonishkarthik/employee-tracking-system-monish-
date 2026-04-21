from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # ── Manager Auth ──────────────────────────────────────────────
    path('',                            views.home,                 name='home'),
    path('register/',                   views.register_view,        name='register'),
    path('login/',                      views.login_view,           name='login'),
    path('logout/',                     views.logout_view,          name='logout'),
    path('forgot-password/',            views.forgot_password_view, name='forgot_password'),
    path('reset-password/<str:token>/', views.reset_password_view,  name='reset_password'),

    # ── Manager Dashboard ─────────────────────────────────────────
    path('dashboard/',                  views.dashboard,            name='dashboard'),
    path('employee/add/',               views.add_employee,         name='add_employee'),
    path('employee/<int:pk>/',          views.employee_detail,      name='employee_detail'),
    path('employee/<int:pk>/edit/',     views.edit_employee,        name='edit_employee'),
    path('employee/<int:pk>/delete/',   views.delete_employee,      name='delete_employee'),

    # ── Custom Admin Panel ────────────────────────────────────────
    path('control/register/',           views.admin_register_view,    name='admin_register'),
    path('control/login/',              views.admin_login_view,        name='admin_login'),
    path('control/logout/',             views.admin_logout_view,       name='admin_logout'),
    path('control/',                    views.admin_dashboard,         name='admin_dashboard'),
    path('control/managers/',           views.admin_managers_list,     name='admin_managers_list'),
    path('control/managers/<int:pk>/',  views.admin_manager_detail,    name='admin_manager_detail'),
    path('control/managers/<int:pk>/delete/', views.admin_delete_manager, name='admin_delete_manager'),
    path('control/employees/',          views.admin_employees_list,    name='admin_employees_list'),
    path('control/employees/<int:pk>/', views.admin_employee_detail,   name='admin_employee_detail'),
    path('control/employees/<int:pk>/delete/', views.admin_delete_employee, name='admin_delete_employee'),
    path('control/admins/',             views.admin_admins_list,       name='admin_admins_list'),
    path('control/admins/<int:pk>/delete/', views.admin_delete_admin,  name='admin_delete_admin'),

    # Forgot Password URLs
    path('password_reset/',
         auth_views.PasswordResetView.as_view(
             template_name='registration/password_reset.html'
         ),
         name='password_reset'),

    path('password_reset_done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html'
         ),
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),

    path('reset_done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html'
         ),
         name='password_reset_complete'),

    path('employee/form/', views.employee_self_form, name='employee_self_form'),
]

from django.contrib.auth import views as auth_views


