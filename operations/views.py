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
        brand_make = request.POST.get('brand_make')
        brand_model = request.POST.get('brand_model')
        product_type = request.POST.get('product_type', '')
        
        if brand_make and brand_model:
            Product.objects.create(
                brand_make=brand_make,
                brand_model=brand_model,
                product_type=product_type
            )
            messages.success(request, f"Product {brand_make} - {brand_model} added!")
            return redirect('product_management')
        else:
            messages.error(request, "Brand Make and Brand Model are required.")
    
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
        return redirect('create_complaint')
    elif action == 'add_engineer':
        return redirect('user_management')
    elif action == 'add_part':
        return redirect('part_management')
    else:
        messages.warning(request, "Invalid action")
        return redirect('operations_dashboard')


# ============================
# CLIENT MANAGEMENT
# ============================
@login_required
def client_management(request):
    """Manage Clients"""
    if not check_operations_access(request.user):
        messages.error(request, "Access denied.")
        return redirect('login')
    
    clients = Client.objects.all().order_by('-created_at')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        primary_contact = request.POST.get('primary_contact_no')
        alternate_contact = request.POST.get('alternate_contact_no', '')
        email = request.POST.get('email', '')
        address = request.POST.get('office_address', '')
        
        if name and primary_contact:
            Client.objects.create(
                name=name,
                primary_contact_no=primary_contact,
                alternate_contact_no=alternate_contact,
                email=email,
                office_address=address
            )
            messages.success(request, f"Client '{name}' added!")
            return redirect('client_management')
        else:
            messages.error(request, "Client name and contact number are required.")
    
    context = {'clients': clients}
    return render(request, 'operations/client_management.html', context)


# ============================
# FAULT MANAGEMENT
# ============================
@login_required
def fault_management(request):
    """Manage Faults"""
    if not check_operations_access(request.user):
        messages.error(request, "Access denied.")
        return redirect('login')
    
    from complaints.models import Fault
    faults = Fault.objects.all().order_by('-created_at')
    
    if request.method == 'POST':
        fault_name = request.POST.get('fault_name')
        description = request.POST.get('description', '')
        
        if fault_name:
            Fault.objects.create(
                fault_name=fault_name,
                description=description
            )
            messages.success(request, f"Fault '{fault_name}' added!")
            return redirect('fault_management')
        else:
            messages.error(request, "Fault name is required.")
    
    context = {'faults': faults}
    return render(request, 'operations/fault_management.html', context)


# ============================
# CREATE COMPLAINT
# ============================
@login_required
def create_complaint(request):
    """Create a new complaint"""
    if not check_operations_access(request.user):
        messages.error(request, "Access denied.")
        return redirect('login')
    
    from complaints.models import Fault
    clients = Client.objects.all().order_by('name')
    products = Product.objects.all().order_by('brand_make')
    faults = Fault.objects.filter(is_active=True).order_by('fault_name')
    
    if request.method == 'POST':
        client_id = request.POST.get('client')
        product_id = request.POST.get('product')
        fault_id = request.POST.get('fault')
        priority = request.POST.get('priority', 'medium')
        other_details = request.POST.get('other_details', '')
        
        if client_id and product_id:
            try:
                client = Client.objects.get(id=client_id)
                product = Product.objects.get(id=product_id)
                fault = Fault.objects.get(id=fault_id) if fault_id else None
                
                complaint = Complaint.objects.create(
                    client=client,
                    product=product,
                    fault=fault,
                    priority=priority,
                    other_details=other_details,
                    status='new'
                )
                messages.success(request, f"Complaint {complaint.complaint_no} created!")
                return redirect('complaint_list')
            except Exception as e:
                messages.error(request, f"Error creating complaint: {str(e)}")
        else:
            messages.error(request, "Client and Product are required.")
    
    context = {
        'clients': clients,
        'products': products,
        'faults': faults,
    }
    return render(request, 'operations/create_complaint.html', context)