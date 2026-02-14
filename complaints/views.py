# from django.shortcuts import render, redirect
# from .models import Complaint, Fault
# from clients.models import Client
# from products.models import Product
# from django.contrib.auth.decorators import login_required
# from django.utils import timezone
#
#
# @login_required
# def add_complaint(request):
#     clients = Client.objects.all()
#     products = Product.objects.all()
#     faults = Fault.objects.filter(is_active=True)
#
#     if request.method == 'POST':
#         client_id = request.POST.get('client')
#         product_id = request.POST.get('product')
#         fault_id = request.POST.get('fault')
#         other_details = request.POST.get('other_details')
#         priority = request.POST.get('priority')
#
#         Complaint.objects.create(
#             client_id=client_id,
#             product_id=product_id,
#             fault_id=fault_id,
#             other_details=other_details,
#             priority=priority
#         )
#
#         return redirect('complaint_list')  # baad me banayenge
#
#     return render(request, 'complaints/assign_complaint.html', {
#         'clients': clients,
#         'products': products,
#         'faults': faults,
#     })

#=================================================================================================================================
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Complaint, ComplaintAssignment
from accounts.models import User


@login_required
def complaint_list(request):
    complaints = Complaint.objects.all().order_by('-created_at')
    return render(request, 'complaints/complaint_list.html', {
        'complaints': complaints
    })


@login_required
def assign_complaint(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)
    engineers = User.objects.filter(role='engineer', is_active=True)

    if request.method == 'POST':
        engineer_id = request.POST.get('engineer')
        remarks = request.POST.get('remarks')

        engineer = get_object_or_404(User, id=engineer_id)

        # create assignment
        ComplaintAssignment.objects.create(
            complaint=complaint,
            engineer=engineer,
            remarks=remarks
        )

        # update complaint status
        complaint.status = 'assigned'
        complaint.save()

        messages.success(request, 'Complaint assigned successfully')
        return redirect('complaint_list')

    return render(request, 'complaints/assign_complaint.html', {
        'complaint': complaint,
        'engineers': engineers
    })
