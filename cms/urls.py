"""
URL configuration for cms project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


# from django.contrib import admin
# from django.urls import path, include
#
# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('', include('accounts.urls')),
#
#     path('complaints/', include('complaints.urls')),
#     path('accounts/', include('accounts.urls')),
# ]


# =========================myproject/urls.py (or urls.py in your main project folder)
# from django.contrib import admin
# from django.urls import path
# from accounts.views import user_login, user_logout, dashboard
#
# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('login/', user_login, name='login'),
#     path('logout/', user_logout, name='logout'),
#     path('dashboard/', dashboard, name='dashboard'),
#
#     # Optional: Make root redirect to login
#     path('', lambda request: redirect('login')),
# ]
#========================================================================================================================
# accounts/urls.py or main urls.py
# myproject/urls.py
from django.contrib import admin
from django.urls import path, include
from accounts.views import user_login, user_logout, admin_dashboard, engineer_dashboard, change_password, profile
from django.shortcuts import redirect

def home_redirect(request):
    if request.user.is_authenticated:
        if request.user.role == 'admin':
            return redirect('admin_dashboard')
        else:
            return redirect('engineer_dashboard')
    return redirect('login')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_redirect, name='home'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('engineer-dashboard/', engineer_dashboard, name='engineer_dashboard'),
    path('change-password/', change_password, name='change_password'),
    path('profile/', profile, name='profile'),
    path('complaints/', include('complaints.urls')),
]
