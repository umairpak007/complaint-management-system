from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta

from complaints.models import Complaint, ComplaintAssignment, ComplaintPartIssue
from accounts.models import User
from inventory.models import Part
from products.models import Product
from clients.models import Client

# Helper function to check access
def check_operations_access(user):
    return user.is_authenticated and user.role in ['admin', 'operations']

@login_required
def operations_dashboard(request):
    """Main Operations Dashboard with real data"""
    if not check_operations_access(request.user):
        messages.error(request, "Access denied. Operations only.")
        return redirect('login')
    
    # Statistics with real data
    total_complaints = Complaint.objects.count()
    pending_complaints = Complaint.objects.filter(status='assigned').count()
    resolved_today = Complaint.objects.filter(
        status='resolved',
        resolved_at__date=timezone.now().date()
    ).count()
    
    active_engineers = User.objects.filter(role='engineer', is_active=True).count()
    total_parts = Part.objects.filter(is_active=True).count()
    low_stock_parts = Part.objects.filter(stock_quantity__lt=5).count()  # if stock field exists
    
    # Recent complaints
    recent_complaints = Complaint.objects.select_related(
        'client', 'product'
    ).order_by('-created_at')[:10]
    
    # Low stock alerts
    low_stock_items = Part.objects.filter(stock_quantity__lt=5)[:5]
    
    context = {
        'total_complaints': total_complaints,
        'pending_complaints': pending_complaints,
        'resolved_today': resolved_today,
        'active_engineers': active_engineers,
        'total_parts': total_parts,
        'low_stock_parts': low_stock_parts,
        'recent_complaints': recent_complaints,
        'low_stock_items': low_stock_items,
    }
    return render(request, 'operations/dashboard.html', context)


@login_required
def user_management(request):
    """Manage Users (Engineers, Operations Staff)"""
    if not check_operations_access(request.user):
        messages.error(request, "Access denied.")
        return redirect('login')
    
    users = User.objects.all().order_by('-date_joined')
    
    if request.method == 'POST':
        # Add new user logic
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        
        if username and email and password:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                role=role
            )
            messages.success(request, f"User {username} created successfully!")
            return redirect('user_management')
    
    context = {
        'users': users,
        'roles': ['engineer', 'operations', 'admin']
    }
    return render(request, 'operations/user_management.html', context)


@login_required
def product_management(request):
    """Manage Products"""
    if not check_operations_access(request.user):
        messages.error(request, "Access denied.")
        return redirect('login')
    
    products = Product.objects.all().order_by('-created_at')
    
    if request.method == 'POST':
        # Add product logic
        name = request.POST.get('name')
        description = request.POST.get('description')
        
        if name:
            Product.objects.create(
                name=name,
                description=description,
                created_by=request.user
            )
            messages.success(request, f"Product {name} added!")
            return redirect('product_management')
    
    context = {'products': products}
    return render(request, 'operations/product_management.html', context)


@login_required
def part_management(request):
    """Manage Parts/Inventory"""
    if not check_operations_access(request.user):
        messages.error(request, "Access denied.")
        return redirect('login')
    
    parts = Part.objects.all().order_by('-id')
    
    if request.method == 'POST':
        # Add part logic
        name = request.POST.get('name')
        make = request.POST.get('make')
        model = request.POST.get('model')
        source = request.POST.get('source')
        stock = request.POST.get('stock_quantity', 0)
        
        if name and make and model:
            Part.objects.create(
                name=name,
                make=make,
                model=model,
                source=source,
                stock_quantity=int(stock) if stock else 0
            )
            messages.success(request, f"Part {name} added!")
            return redirect('part_management')
    
    context = {'parts': parts}
    return render(request, 'operations/part_management.html', context)


@login_required
def pending_complaints(request):
    """View all pending complaints"""
    if not check_operations_access(request.user):
        messages.error(request, "Access denied.")
        return redirect('login')
    
    complaints = Complaint.objects.filter(
        status='assigned'
    ).select_related('client', 'product').order_by('-created_at')
    
    context = {'complaints': complaints}
    return render(request, 'operations/pending_complaints.html', context)


@login_required
def inventory_alerts(request):
    """View all low stock items"""
    if not check_operations_access(request.user):
        messages.error(request, "Access denied.")
        return redirect('login')
    
    low_stock = Part.objects.filter(stock_quantity__lt=5)
    out_of_stock = Part.objects.filter(stock_quantity=0)
    
    context = {
        'low_stock': low_stock,
        'out_of_stock': out_of_stock,
    }
    return render(request, 'operations/inventory_alerts.html', context)


@login_required
def quick_actions(request):
    """Handle quick actions via AJAX or redirects"""
    if not check_operations_access(request.user):
        messages.error(request, "Access denied.")
        return redirect('login')
    
    action = request.GET.get('action')
    
    if action == 'new_complaint':
        return redirect('complaint_list')  # or your complaint create URL
    elif action == 'add_engineer':
        return redirect('user_management')
    elif action == 'add_part':
        return redirect('part_management')
    else:
        messages.warning(request, "Invalid action")
        return redirect('operations_dashboard')