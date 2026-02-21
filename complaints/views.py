# #this is views.py file for complaints app
# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from django.db import transaction
# from django.utils import timezone
# from django.db.models import Q
# from django.http import JsonResponse
# from django.contrib.auth.mixins import UserPassesTestMixin
# from django.views.generic import ListView, DetailView, UpdateView
# from django.urls import reverse_lazy

# from .models import Complaint, ComplaintAssignment, ComplaintPartIssue
# from accounts.models import User
# from inventory.models import Part
# from .forms import ComplaintResolutionForm, ComplaintStatusUpdateForm, part_usage_formset_factory

# # ============================
# # EXISTING VIEWS (Aapke purane)
# # ============================

# @login_required
# def complaint_list(request):
#     """List all complaints (Admin view)"""
#     complaints = Complaint.objects.all().order_by('-created_at')
#     return render(request, 'complaints/complaint_list.html', {
#         'complaints': complaints
#     })


# @login_required
# def assign_complaint(request, pk):
#     """Assign complaint to engineer with parts"""
#     complaint = get_object_or_404(Complaint, pk=pk)

#     # Check if already assigned
#     if complaint.status == 'assigned':
#         messages.error(request, "This complaint is already assigned and cannot be reassigned.")
#         return redirect('complaint_list')

#     # Get all active engineers
#     engineers = User.objects.filter(role='engineer', is_active=True)
    
#     # Get all active parts
#     parts = Part.objects.filter(is_active=True)

#     if request.method == 'POST':
#         # Get engineer and remarks from POST
#         engineer_id = request.POST.get('engineer')
#         remarks = request.POST.get('remarks')

#         if not engineer_id:
#             messages.error(request, "Please select an engineer.")
#             return redirect('assign_complaint', pk=pk)

#         engineer = get_object_or_404(User, id=engineer_id)

#         # Create assignment
#         assignment = ComplaintAssignment.objects.create(
#             complaint=complaint,
#             engineer=engineer,
#             remarks=remarks,
#             is_active=True
#         )

#         # Get part data from POST
#         part_ids = request.POST.getlist('part')
#         quantities = request.POST.getlist('quantity')
#         sources = request.POST.getlist('source')
#         notes_list = request.POST.getlist('notes')

#         # Create part issues
#         parts_issued = False
        
#         if part_ids and quantities and sources:
#             for i in range(len(part_ids)):
#                 part_id = part_ids[i]
#                 qty = quantities[i] if i < len(quantities) else ''
#                 source = sources[i] if i < len(sources) else ''
#                 note = notes_list[i] if i < len(notes_list) else ''
                
#                 if part_id and qty and source:
#                     try:
#                         part = Part.objects.get(id=part_id)
#                         ComplaintPartIssue.objects.create(
#                             assignment=assignment,
#                             part=part,
#                             quantity=int(qty),
#                             source=source,
#                             notes=note
#                         )
#                         parts_issued = True
#                     except Part.DoesNotExist:
#                         messages.warning(request, f"Part ID {part_id} not found, skipping...")
#                     except Exception as e:
#                         messages.warning(request, f"Error issuing part: {str(e)}")

#         if not parts_issued:
#             messages.warning(request, "No parts were issued with this assignment.")

#         # Update complaint status
#         complaint.status = 'assigned'
#         complaint.save()

#         messages.success(request, f"Complaint assigned to {engineer.username} successfully!")
#         return redirect('complaint_list')

#     return render(request, 'complaints/assign_complaint.html', {
#         'complaint': complaint,
#         'engineers': engineers,
#         'parts': parts
#     })


# # ============================
# # NEW VIEWS (Engineer Features)
# # ============================

# class EngineerRequiredMixin(UserPassesTestMixin):
#     """Mixin to ensure only engineers can access"""
#     def test_func(self):
#         return self.request.user.is_authenticated and self.request.user.role == 'engineer'



# @login_required
# def engineer_dashboard(request):
#     """Dashboard for engineers - shows their assigned complaints"""
#     print("="*50)
#     print("ENGINEER DASHBOARD VIEW CALLED")
#     print(f"User: {request.user}")
#     print(f"Is authenticated: {request.user.is_authenticated}")
#     print(f"Path: {request.path}")
#     print("="*50)
    
#     # Role check with proper error handling
#     if not hasattr(request.user, 'role'):
#         messages.error(request, "User role not defined. Please contact admin.")
#         return redirect('login')
    
#     if request.user.role != 'engineer':
#         messages.error(request, "Access denied. Engineers only.")
#         return redirect('complaint_list')
    
#     # Get complaints assigned to this engineer
#     complaints = Complaint.objects.filter(
#         assignments__engineer=request.user,
#         assignments__is_active=True
#     ).select_related('client', 'product').order_by('-created_at')
    
#     # Statistics
#     total = complaints.count()
#     pending = complaints.filter(status='assigned').count()
#     resolved = complaints.filter(status='resolved').count()
    
#     context = {
#         'complaints': complaints,
#         'total_complaints': total,
#         'pending_complaints': pending,
#         'resolved_complaints': resolved,
#     }
#     return render(request, 'complaints/engineer_dashboard.html', context)


# @login_required
# def engineer_complaint_detail(request, pk):
#     """Engineer views complaint details"""
#     if request.user.role != 'engineer':
#         messages.error(request, "Access denied.")
#         return redirect('complaint_list')
    
#     # Ensure complaint is assigned to this engineer
#     complaint = get_object_or_404(
#         Complaint.objects.filter(
#             assignments__engineer=request.user,
#             assignments__is_active=True
#         ).select_related('client', 'product', 'fault'),
#         pk=pk
#     )
    
#     # Get issued parts
#     issued_parts = ComplaintPartIssue.objects.filter(
#         assignment__complaint=complaint
#     ).select_related('part')
    
#     context = {
#         'complaint': complaint,
#         'issued_parts': issued_parts,
#     }
#     return render(request, 'complaints/engineer_complaint_detail.html', context)



# @login_required
# @transaction.atomic
# def resolve_complaint(request, pk):
#     """
#     Engineer resolves complaint with parts usage and charges
#     """
#     if request.user.role != 'engineer':
#         messages.error(request, "Access denied.")
#         return redirect('complaint_list')
    
#     # Get complaint assigned to this engineer
#     complaint = get_object_or_404(
#         Complaint.objects.filter(
#             assignments__engineer=request.user,
#             assignments__is_active=True,
#             status='assigned'
#         ),
#         pk=pk
#     )
    
#     # Get issued parts for this complaint
#     issued_parts = ComplaintPartIssue.objects.filter(
#         assignment__complaint=complaint
#     ).select_related('part')
    
#     if request.method == 'POST':
#         try:
#             with transaction.atomic():
#                 # Get form data
#                 service_charge = float(request.POST.get('service_charge', 0))
#                 is_free = request.POST.get('is_free') == 'on'
#                 is_amc = request.POST.get('is_amc') == 'on'
#                 is_warranty = request.POST.get('is_warranty') == 'on'
#                 remarks = request.POST.get('resolution_remarks', '')
                
#                 # Validate special cases
#                 special_count = sum([is_free, is_amc, is_warranty])
#                 if special_count > 1:
#                     messages.error(request, "Select only one: Free, AMC, or Warranty")
#                     return redirect('resolve_complaint', pk=pk)
                
#                 # Process parts usage
#                 total_parts_cost = 0
                
#                 for part_issue in issued_parts:
#                     # Get quantity and price from POST
#                     used_qty = int(request.POST.get(f'used_qty_{part_issue.id}', 0))
#                     user_price = float(request.POST.get(f'price_{part_issue.id}', 0))
                    
#                     if used_qty > 0:
#                         # 🔥 OPTION A: Stock check hata do agar field nahi hai
#                         # part = Part.objects.get(id=part_issue.part.id)
                        
#                         # 🔥 OPTION B: Stock check with try/except
#                         try:
#                             part = Part.objects.get(id=part_issue.part.id)
#                             # Agar stock_quantity field hai to check karo
#                             if hasattr(part, 'stock_quantity'):
#                                 if part.stock_quantity < used_qty:
#                                     messages.error(request, f"Insufficient stock for {part.name}")
#                                     return redirect('resolve_complaint', pk=pk)
#                                 # Deduct from inventory
#                                 part.stock_quantity -= used_qty
#                                 part.save()
#                         except Exception as e:
#                             print(f"Stock check skipped: {e}")
                        
#                         # Update part issue
#                         part_issue.used_quantity = used_qty
#                         part_issue.usage_status = 'used'
#                         part_issue.part_cost_at_time = user_price
#                         part_issue.save()
                        
#                         # Calculate cost
#                         total_parts_cost += used_qty * user_price
                
#                 # Update complaint
#                 complaint.status = 'resolved'
#                 complaint.service_charge = service_charge if not (is_free or is_amc or is_warranty) else 0
#                 complaint.total_parts_cost = total_parts_cost
#                 complaint.is_free = is_free
#                 complaint.is_amc = is_amc
#                 complaint.is_warranty = is_warranty
#                 complaint.resolution_remarks = remarks
#                 complaint.resolved_at = timezone.now()
#                 complaint.resolved_by = request.user
                
#                 # Grand total calculation
#                 if is_free or is_amc or is_warranty:
#                     complaint.grand_total = 0
#                 else:
#                     complaint.grand_total = complaint.service_charge + complaint.total_parts_cost
                
#                 complaint.save()
                
#                 messages.success(request, f"Complaint #{complaint.complaint_no} resolved successfully!")
#                 return redirect('engineer_dashboard')
                
#         except Exception as e:
#             messages.error(request, f"Error: {str(e)}")
#             return redirect('resolve_complaint', pk=pk)
    
#     # GET request - show form
#     context = {
#         'complaint': complaint,
#         'issued_parts': issued_parts,
#     }
#     return render(request, 'complaints/resolve_complaint.html', context)



# @login_required
# def update_complaint_status(request, pk):
#     """
#     Engineer updates status to visit_only or cancel
#     """
#     if request.user.role != 'engineer':
#         messages.error(request, "Access denied.")
#         return redirect('complaint_list')
    
#     complaint = get_object_or_404(
#         Complaint.objects.filter(
#             assignments__engineer=request.user,
#             assignments__is_active=True,
#             status='assigned'
#         ),
#         pk=pk
#     )
    
#     if request.method == 'POST':
#         new_status = request.POST.get('status')
#         remarks = request.POST.get('remarks', '')
        
#         if new_status in ['visit_only', 'cancel']:
#             complaint.status = new_status
#             complaint.resolution_remarks = remarks
#             complaint.resolved_at = timezone.now()
#             complaint.resolved_by = request.user
#             complaint.save()
            
#             messages.info(request, f"Complaint marked as {complaint.get_status_display()}")
#             return redirect('engineer_dashboard')
#         else:
#             messages.error(request, "Invalid status")
    
#     return render(request, 'complaints/update_status.html', {'complaint': complaint})


# # ============================
# # AJAX Views for Dynamic Calculations
# # ============================

# @login_required
# def calculate_part_cost_ajax(request):
#     """AJAX endpoint to calculate part cost on quantity change"""
#     if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#         part_id = request.POST.get('part_id')
#         quantity = int(request.POST.get('quantity', 0))
        
#         try:
#             part = Part.objects.get(id=part_id)
#             cost = (part.selling_price or part.purchase_cost or 0) * quantity
            
#             return JsonResponse({
#                 'success': True,
#                 'cost': float(cost),
#                 'available': part.stock_quantity,
#                 'price_per_unit': float(part.selling_price or part.purchase_cost or 0)
#             })
#         except Part.DoesNotExist:
#             return JsonResponse({'success': False, 'error': 'Part not found'})
    
#     return JsonResponse({'success': False, 'error': 'Invalid request'})



# this is views.py file for complaints app
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import ListView, DetailView, UpdateView
from django.urls import reverse_lazy

from .models import Complaint, ComplaintAssignment, ComplaintPartIssue
from accounts.models import User
from inventory.models import Part
from .forms import ComplaintResolutionForm, ComplaintStatusUpdateForm, part_usage_formset_factory

# ============================
# EXISTING VIEWS (Aapke purane)
# ============================

@login_required
def complaint_list(request):
    """List all complaints (Admin view)"""
    complaints = Complaint.objects.all().order_by('-created_at')
    return render(request, 'complaints/complaint_list.html', {
        'complaints': complaints
    })


@login_required
def assign_complaint(request, pk):
    """Assign complaint to engineer with parts"""
    complaint = get_object_or_404(Complaint, pk=pk)

    # Check if already assigned
    if complaint.status == 'assigned':
        messages.error(request, "This complaint is already assigned and cannot be reassigned.")
        return redirect('complaint_list')

    # Get all active engineers
    engineers = User.objects.filter(role='engineer', is_active=True)
    
    # Get all active parts
    parts = Part.objects.filter(is_active=True)

    if request.method == 'POST':
        # Get engineer and remarks from POST
        engineer_id = request.POST.get('engineer')
        remarks = request.POST.get('remarks')

        if not engineer_id:
            messages.error(request, "Please select an engineer.")
            return redirect('assign_complaint', pk=pk)

        engineer = get_object_or_404(User, id=engineer_id)

        # Create assignment
        assignment = ComplaintAssignment.objects.create(
            complaint=complaint,
            engineer=engineer,
            remarks=remarks,
            is_active=True
        )

        # Get part data from POST
        part_ids = request.POST.getlist('part')
        quantities = request.POST.getlist('quantity')
        sources = request.POST.getlist('source')
        notes_list = request.POST.getlist('notes')

        # Create part issues
        parts_issued = False
        
        if part_ids and quantities and sources:
            for i in range(len(part_ids)):
                part_id = part_ids[i]
                qty = quantities[i] if i < len(quantities) else ''
                source = sources[i] if i < len(sources) else ''
                note = notes_list[i] if i < len(notes_list) else ''
                
                if part_id and qty and source:
                    try:
                        part = Part.objects.get(id=part_id)
                        ComplaintPartIssue.objects.create(
                            assignment=assignment,
                            part=part,
                            quantity=int(qty),
                            source=source,
                            notes=note
                        )
                        parts_issued = True
                    except Part.DoesNotExist:
                        messages.warning(request, f"Part ID {part_id} not found, skipping...")
                    except Exception as e:
                        messages.warning(request, f"Error issuing part: {str(e)}")

        if not parts_issued:
            messages.warning(request, "No parts were issued with this assignment.")

        # Update complaint status
        complaint.status = 'assigned'
        complaint.save()

        messages.success(request, f"Complaint assigned to {engineer.username} successfully!")
        return redirect('complaint_list')

    return render(request, 'complaints/assign_complaint.html', {
        'complaint': complaint,
        'engineers': engineers,
        'parts': parts
    })


# ============================
# ENGINEER VIEWS
# ============================

class EngineerRequiredMixin(UserPassesTestMixin):
    """Mixin to ensure only engineers can access"""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'engineer'


@login_required
def engineer_dashboard(request):
    """Dashboard for engineers - shows their assigned complaints"""
    print("="*50)
    print("ENGINEER DASHBOARD VIEW CALLED")
    print(f"User: {request.user}")
    print(f"Is authenticated: {request.user.is_authenticated}")
    print(f"Path: {request.path}")
    print("="*50)
    
    # Role check with proper error handling
    if not hasattr(request.user, 'role'):
        messages.error(request, "User role not defined. Please contact admin.")
        return redirect('login')
    
    if request.user.role != 'engineer':
        messages.error(request, "Access denied. Engineers only.")
        return redirect('complaint_list')
    
    # Get complaints assigned to this engineer
    complaints = Complaint.objects.filter(
        assignments__engineer=request.user,
        assignments__is_active=True
    ).select_related('client', 'product').order_by('-created_at')
    
    # Statistics
    total = complaints.count()
    pending = complaints.filter(status='assigned').count()
    resolved = complaints.filter(status='resolved').count()
    
    context = {
        'complaints': complaints,
        'total_complaints': total,
        'pending_complaints': pending,
        'resolved_complaints': resolved,
    }
    return render(request, 'complaints/engineer_dashboard.html', context)


@login_required
def engineer_complaint_detail(request, pk):
    """Engineer views complaint details"""
    if request.user.role != 'engineer':
        messages.error(request, "Access denied.")
        return redirect('complaint_list')
    
    # Ensure complaint is assigned to this engineer
    complaint = get_object_or_404(
        Complaint.objects.filter(
            assignments__engineer=request.user,
            assignments__is_active=True
        ).select_related('client', 'product', 'fault'),
        pk=pk
    )
    
    # Get issued parts
    issued_parts = ComplaintPartIssue.objects.filter(
        assignment__complaint=complaint
    ).select_related('part')
    
    context = {
        'complaint': complaint,
        'issued_parts': issued_parts,
    }
    return render(request, 'complaints/engineer_complaint_detail.html', context)


# ============================
# RESOLVE COMPLAINT VIEW (FIXED WITH PART RETURN LOGIC)
# ============================

@login_required
@transaction.atomic
def resolve_complaint(request, pk):
    """
    Engineer resolves complaint with parts usage, return, and charges
    """
    if request.user.role != 'engineer':
        messages.error(request, "Access denied.")
        return redirect('complaint_list')
    
    # Get complaint assigned to this engineer
    complaint = get_object_or_404(
        Complaint.objects.filter(
            assignments__engineer=request.user,
            assignments__is_active=True,
            status='assigned'
        ),
        pk=pk
    )
    
    # Get issued parts for this complaint
    issued_parts = ComplaintPartIssue.objects.filter(
        assignment__complaint=complaint
    ).select_related('part')
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Get form data
                service_charge = float(request.POST.get('service_charge', 0))
                is_free = request.POST.get('is_free') == 'on'
                is_amc = request.POST.get('is_amc') == 'on'
                is_warranty = request.POST.get('is_warranty') == 'on'
                remarks = request.POST.get('resolution_remarks', '')
                
                # Validate special cases
                special_count = sum([is_free, is_amc, is_warranty])
                if special_count > 1:
                    messages.error(request, "Select only one: Free, AMC, or Warranty")
                    return redirect('resolve_complaint', pk=pk)
                
                # Process parts usage and return
                total_parts_cost = 0
                parts_used_count = 0
                parts_returned_count = 0
                
                for part_issue in issued_parts:
                    # Get data from POST
                    used_qty = int(request.POST.get(f'used_qty_{part_issue.id}', 0))
                    user_price = float(request.POST.get(f'price_{part_issue.id}', 0))
                    remaining_qty = int(request.POST.get(f'remaining_qty_{part_issue.id}', 0))
                    is_returned = request.POST.get(f'return_{part_issue.id}') == 'on'
                    
                    # Get the part for inventory update
                    part = part_issue.part
                    
                    if used_qty > 0:
                        # Parts used in service
                        part_issue.used_quantity = used_qty
                        part_issue.usage_status = 'used'
                        part_issue.part_cost_at_time = user_price
                        part_issue.save()
                        
                        # Add to total cost
                        total_parts_cost += used_qty * user_price
                        parts_used_count += used_qty
                        
                        # Deduct used parts from inventory (if stock management exists)
                        if hasattr(part, 'stock_quantity'):
                            part.stock_quantity -= used_qty
                            part.save()
                    
                    # Handle returned parts
                    if is_returned and remaining_qty > 0:
                        # Update original part issue status
                        part_issue.usage_status = 'partial_return' if used_qty > 0 else 'returned'
                        part_issue.save()
                        
                        # Add returned parts back to inventory
                        if hasattr(part, 'stock_quantity'):
                            part.stock_quantity += remaining_qty
                            part.save()
                        
                        parts_returned_count += remaining_qty
                        
                        # Optional: Create a return record
                        # You can create a separate model for returns if needed
                
                # Update complaint
                complaint.status = 'resolved'
                complaint.service_charge = service_charge if not (is_free or is_amc or is_warranty) else 0
                complaint.total_parts_cost = total_parts_cost
                complaint.is_free = is_free
                complaint.is_amc = is_amc
                complaint.is_warranty = is_warranty
                complaint.resolution_remarks = remarks
                complaint.resolved_at = timezone.now()
                complaint.resolved_by = request.user
                
                # Calculate grand total
                if is_free or is_amc or is_warranty:
                    complaint.grand_total = 0
                else:
                    complaint.grand_total = complaint.service_charge + complaint.total_parts_cost
                
                complaint.save()
                
                # Success message with summary
                summary = f"Complaint #{complaint.complaint_no} resolved! "
                if parts_used_count > 0:
                    summary += f"{parts_used_count} parts used. "
                if parts_returned_count > 0:
                    summary += f"{parts_returned_count} parts returned."
                
                messages.success(request, summary)
                return redirect('engineer_dashboard')
                
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return redirect('resolve_complaint', pk=pk)
    
    # GET request - show form
    context = {
        'complaint': complaint,
        'issued_parts': issued_parts,
    }
    return render(request, 'complaints/resolve_complaint.html', context)


# ============================
# UPDATE STATUS VIEW
# ============================

@login_required
def update_complaint_status(request, pk):
    """
    Engineer updates status to visit_only or cancel
    """
    if request.user.role != 'engineer':
        messages.error(request, "Access denied.")
        return redirect('complaint_list')
    
    complaint = get_object_or_404(
        Complaint.objects.filter(
            assignments__engineer=request.user,
            assignments__is_active=True,
            status='assigned'
        ),
        pk=pk
    )
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        remarks = request.POST.get('remarks', '')
        
        if new_status in ['visit_only', 'cancel']:
            complaint.status = new_status
            complaint.resolution_remarks = remarks
            complaint.resolved_at = timezone.now()
            complaint.resolved_by = request.user
            complaint.save()
            
            messages.info(request, f"Complaint marked as {complaint.get_status_display()}")
            return redirect('engineer_dashboard')
        else:
            messages.error(request, "Invalid status")
    
    return render(request, 'complaints/update_status.html', {'complaint': complaint})


# ============================
# AJAX VIEWS FOR DYNAMIC CALCULATIONS
# ============================

@login_required
def calculate_part_cost_ajax(request):
    """AJAX endpoint to calculate part cost on quantity change"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        part_id = request.POST.get('part_id')
        quantity = int(request.POST.get('quantity', 0))
        
        try:
            part = Part.objects.get(id=part_id)
            
            return JsonResponse({
                'success': True,
                'available': getattr(part, 'stock_quantity', 0),
                'price_per_unit': 0  # User will enter price manually
            })
        except Part.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Part not found'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})
