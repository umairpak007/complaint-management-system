# this is urls.py file for cms project
# from django.contrib import admin
# from django.urls import path, include
# from accounts.views import user_login, user_logout, admin_dashboard, engineer_dashboard, change_password, profile
# from django.shortcuts import redirect

# def home_redirect(request):
#     if request.user.is_authenticated:
#         if request.user.role == 'admin':
#             return redirect('admin_dashboard')
#         else:
#             return redirect('engineer_dashboard')
#     return redirect('login')

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('', home_redirect, name='home'),
#     path('login/', user_login, name='login'),
#     path('logout/', user_logout, name='logout'),
#     path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
#     path('engineer-dashboard/', engineer_dashboard, name='engineer_dashboard'),
#     path('change-password/', change_password, name='change_password'),
#     path('profile/', profile, name='profile'),
#     path('complaints/', include('complaints.urls')),
# ]
# here i m creating 2 admin pennal aproch -----------------------------------------------------------------
from django.contrib import admin
from django.urls import path, include
from accounts.views import user_login, user_logout, admin_dashboard, engineer_dashboard, change_password, profile
from django.shortcuts import redirect

def home_redirect(request):
    if request.user.is_authenticated:
        if request.user.role == 'admin':
            return redirect('admin_dashboard')
        elif request.user.role == 'engineer':
            return redirect('engineer_dashboard')
        elif request.user.role == 'operations':
            return redirect('operations_dashboard')
        elif request.user.role == 'analytics':
            return redirect('analytics_dashboard')
    return redirect('login')

urlpatterns = [
    # Root → redirect by role (or to login)
    path('', home_redirect, name='home'),

    # Existing Admin (Django built-in)
    path('admin/', admin.site.urls),
    
    # Authentication
    path('accounts/login/', user_login, name='login'),
    path('accounts/logout/', user_logout, name='logout'),
    path('accounts/change-password/', change_password, name='change_password'),
    path('accounts/profile/', profile, name='profile'),
    
    # Existing Dashboards
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('engineer-dashboard/', engineer_dashboard, name='engineer_dashboard'),
    
    # ==========================================
    # NEW DUAL ADMIN PANELS
    # ==========================================
    
    # Panel 1: Operational Admin (For daily work)
    path('operations/', include('operations.urls')),
    
    # Panel 2: Reporting & Analytics (For management)
    path('analytics/', include('analytics.urls')),
    
    # Complaints App (keep as is)
    path('complaints/', include('complaints.urls')),
]
