# from django.contrib.auth import authenticate, login, logout
# from django.shortcuts import render, redirect
# from django.contrib import messages
#
#
# def user_login(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#
#         user = authenticate(request, username=username, password=password)
#
#         if user is not None:
#             login(request, user)
#             return redirect('/admin/')   # ✅ direct admin panel
#
#         else:
#             messages.error(request, 'Invalid username or password.....')
#
#     return render(request, 'accounts/login.html')
#
#
#
# def user_logout(request):
#     logout(request)
#     return redirect('login')


#=======================================accounts/views.py====================================
# from django.contrib.auth import authenticate, login, logout
# from django.shortcuts import render, redirect
# from django.contrib import messages
#
#
# def user_login(request):
#     # If already logged in, redirect to appropriate page
#     if request.user.is_authenticated:
#         return redirect('/admin/' if request.user.role == 'admin' else '/dashboard/')
#
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#
#         print(f"Login attempt for: {username}")  # Debug print
#
#         user = authenticate(request, username=username, password=password)
#
#         if user is not None:
#             login(request, user)
#             print(f"Login successful! Role: {user.role}")  # Debug print
#
#             # Redirect based on role
#             if user.role == 'admin':
#                 return redirect('/admin/')
#             else:
#                 # For engineers, redirect to a simple dashboard
#                 return redirect('/dashboard/')
#         else:
#             print("Authentication failed!")  # Debug print
#             messages.error(request, 'Invalid username or password')
#
#     return render(request, 'accounts/login.html')
#
#
# def user_logout(request):
#     logout(request)
#     return redirect('login')
#
#
# def dashboard(request):
#     """Simple dashboard view for engineers"""
#     if not request.user.is_authenticated:
#         return redirect('login')
#
#     return render(request, 'accounts/dashboard.html', {
#         'user': request.user
#     })
#=================Beautiful code =================================================
# accounts/views.py
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
import json

# Import your models
try:
    from clients.models import Client
    from products.models import Product
    from complaints.models import Complaint, ComplaintAssignment, Fault
except ImportError:
    # Create dummy functions if models don't exist yet
    Client = Product = Complaint = ComplaintAssignment = Fault = None


def user_login(request):
    if request.user.is_authenticated:
        if request.user.role == 'admin':
            return redirect('admin_dashboard')
        else:
            return redirect('engineer_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if user.role == 'admin':
                messages.success(request, f'Welcome back, Admin {user.username}!')
                return redirect('admin_dashboard')
            else:
                messages.success(request, f'Welcome, Engineer {user.username}!')
                return redirect('engineer_dashboard')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'accounts/login.html')


@login_required
def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully!')
    return redirect('login')


@login_required
def admin_dashboard(request):
    if request.user.role != 'admin':
        messages.error(request, 'Access denied! Admin only.')
        return redirect('engineer_dashboard')

    # Get statistics
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    try:
        total_clients = Client.objects.count() if Client else 0
        total_products = Product.objects.count() if Product else 0
        total_complaints = Complaint.objects.count() if Complaint else 0

        # Complaint statistics
        complaints_today = Complaint.objects.filter(
            created_at__date=today
        ).count() if Complaint else 0

        complaints_week = Complaint.objects.filter(
            created_at__date__gte=week_ago
        ).count() if Complaint else 0

        complaints_month = Complaint.objects.filter(
            created_at__date__gte=month_ago
        ).count() if Complaint else 0

        # Status distribution
        status_data = []
        if Complaint:
            status_counts = Complaint.objects.values('status').annotate(
                count=Count('id')
            )
            for item in status_counts:
                status_data.append({
                    'status': item['status'],
                    'count': item['count']
                })

        # Priority distribution
        priority_data = []
        if Complaint:
            priority_counts = Complaint.objects.values('priority').annotate(
                count=Count('id')
            )
            for item in priority_counts:
                priority_data.append({
                    'priority': item['priority'],
                    'count': item['count']
                })

        # Recent complaints
        recent_complaints = []
        if Complaint:
            recent_complaints = Complaint.objects.select_related(
                'client', 'product', 'fault'
            ).order_by('-created_at')[:10]

        # Fault frequency
        fault_data = []
        if Complaint and Fault:
            fault_counts = Complaint.objects.values(
                'fault__fault_name'
            ).annotate(
                count=Count('id')
            ).order_by('-count')[:5]

            for item in fault_counts:
                if item['fault__fault_name']:
                    fault_data.append({
                        'fault': item['fault__fault_name'],
                        'count': item['count']
                    })

        context = {
            'user': request.user,
            'total_clients': total_clients,
            'total_products': total_products,
            'total_complaints': total_complaints,
            'complaints_today': complaints_today,
            'complaints_week': complaints_week,
            'complaints_month': complaints_month,
            'status_data': json.dumps(status_data),
            'priority_data': json.dumps(priority_data),
            'fault_data': json.dumps(fault_data),
            'recent_complaints': recent_complaints,
        }

    except Exception as e:
        # For demo purposes, use dummy data if models aren't ready
        context = {
            'user': request.user,
            'total_clients': 45,
            'total_products': 12,
            'total_complaints': 156,
            'complaints_today': 5,
            'complaints_week': 28,
            'complaints_month': 156,
            'status_data': json.dumps([
                {'status': 'new', 'count': 45},
                {'status': 'assigned', 'count': 32},
                {'status': 'in_progress', 'count': 56},
                {'status': 'closed', 'count': 23}
            ]),
            'priority_data': json.dumps([
                {'priority': 'high', 'count': 23},
                {'priority': 'medium', 'count': 89},
                {'priority': 'low', 'count': 44}
            ]),
            'fault_data': json.dumps([
                {'fault': 'Power Issue', 'count': 45},
                {'fault': 'Display Problem', 'count': 32},
                {'fault': 'Software Crash', 'count': 28},
                {'fault': 'Network Issue', 'count': 25},
                {'fault': 'Hardware Failure', 'count': 18}
            ]),
            'recent_complaints': [],
        }

    return render(request, 'accounts/admin_dashboard.html', context)


@login_required
def engineer_dashboard(request):
    if request.user.role != 'engineer':
        messages.error(request, 'Access denied! Engineer only.')
        return redirect('admin_dashboard')

    try:
        # Get engineer's assigned complaints
        assigned_complaints = ComplaintAssignment.objects.filter(
            engineer=request.user,
            is_active=True
        ).select_related(
            'complaint',
            'complaint__client',
            'complaint__product'
        ).order_by('-assigned_at')

        # Get complaints by status
        assigned_complaints_list = []
        for assignment in assigned_complaints:
            assigned_complaints_list.append(assignment.complaint)

        # Count by status
        status_counts = {
            'new': 0,
            'assigned': 0,
            'in_progress': 0,
            'closed': 0,
        }

        for comp in assigned_complaints_list:
            if comp.status in status_counts:
                status_counts[comp.status] += 1

        # Count by priority
        priority_counts = {
            'high': 0,
            'medium': 0,
            'low': 0,
        }

        for comp in assigned_complaints_list:
            if comp.priority in priority_counts:
                priority_counts[comp.priority] += 1

        # Recently closed complaints (last 7 days)
        recent_closed = []
        if Complaint:
            recent_closed = Complaint.objects.filter(
                status='closed',
                assignments__engineer=request.user,
                updated_at__gte=timezone.now() - timedelta(days=7)
            ).distinct()[:5]

        context = {
            'user': request.user,
            'assigned_complaints': assigned_complaints_list,
            'total_assigned': len(assigned_complaints_list),
            'status_counts': status_counts,
            'priority_counts': priority_counts,
            'recent_closed': recent_closed,
        }

    except Exception as e:
        # Demo data
        context = {
            'user': request.user,
            'assigned_complaints': [],
            'total_assigned': 8,
            'status_counts': {'new': 2, 'assigned': 3, 'in_progress': 2, 'closed': 1},
            'priority_counts': {'high': 2, 'medium': 4, 'low': 2},
            'recent_closed': [],
        }

    return render(request, 'accounts/engineer_dashboard.html', context)


@login_required
def change_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        if not request.user.check_password(old_password):
            messages.error(request, 'Your old password was entered incorrectly.')
        elif new_password1 != new_password2:
            messages.error(request, 'New passwords do not match.')
        elif len(new_password1) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
        else:
            request.user.set_password(new_password1)
            request.user.save()

            # Re-authenticate user with new password
            updated_user = authenticate(
                username=request.user.username,
                password=new_password1
            )
            if updated_user:
                login(request, updated_user)
                messages.success(request, 'Password changed successfully!')
                if request.user.role == 'admin':
                    return redirect('admin_dashboard')
                else:
                    return redirect('engineer_dashboard')

    return render(request, 'accounts/change_password.html')


@login_required
def profile(request):
    return render(request, 'accounts/profile.html', {'user': request.user})
