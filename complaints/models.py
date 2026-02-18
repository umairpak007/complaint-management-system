# from django.db import models
# from django.utils import timezone
# from django.conf import settings

# from clients.models import Client
# from products.models import Product
# from inventory.models import Part   # ✅ Correct app

# # from inventory.models import Part  # change if your Part model is in another app


# # =========================
# # Fault Master Table
# # =========================
# class Fault(models.Model):
#     fault_name = models.CharField(max_length=100, unique=True)
#     description = models.TextField(blank=True, null=True)
#     is_active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.fault_name


# # =========================
# # Complaint
# # =========================
# class Complaint(models.Model):

#     STATUS_CHOICES = (
#         ('new', 'New'),
#         ('assigned', 'Assigned'),
#         ('in_progress', 'In Progress'),
#         ('closed', 'Closed'),
#     )

#     PRIORITY_CHOICES = (
#         ('low', 'Low'),
#         ('medium', 'Medium'),
#         ('high', 'High'),
#     )

#     complaint_no = models.CharField(max_length=20, unique=True, editable=False)
#     client = models.ForeignKey(Client, on_delete=models.CASCADE)
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)

#     # Fixed: Only one fault field defined
#     fault = models.ForeignKey(
#         Fault,
#         on_delete=models.PROTECT,
#         null=True,
#         blank=True
#     )

#     other_details = models.TextField(blank=True, default='')

#     status = models.CharField(
#         max_length=20,
#         choices=STATUS_CHOICES,
#         default='new'
#     )

#     priority = models.CharField(
#         max_length=20,
#         choices=PRIORITY_CHOICES,
#         default='medium'
#     )

#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def save(self, *args, **kwargs):
#         if not self.complaint_no:
#             year = timezone.now().year
#             last = Complaint.objects.filter(
#                 complaint_no__startswith=f"CMP-{year}"
#             ).count() + 1
#             self.complaint_no = f"CMP-{year}-{last:04d}"
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return self.complaint_no


# # =========================
# # Complaint Assignment
# # =========================
# class ComplaintAssignment(models.Model):
#     complaint = models.ForeignKey(
#         Complaint,
#         on_delete=models.CASCADE,
#         related_name='assignments'
#     )

#     engineer = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         limit_choices_to={'role': 'engineer'}
#     )

#     assigned_at = models.DateTimeField(auto_now_add=True)
#     remarks = models.TextField(blank=True, null=True)
#     is_active = models.BooleanField(default=True)

#     def __str__(self):
#         return f"{self.complaint} → {self.engineer}"
    
# # =========================
# # Parts Issue To Engineer
# # =========================
# class ComplaintPartIssue(models.Model):
#     SOURCE_CHOICES = (
#         ('new', 'New'),
#         ('used', 'Used'),
#         ('outsource', 'Outsource'),
#     )
    
#     assignment = models.ForeignKey(
#         'ComplaintAssignment',
#         on_delete=models.CASCADE,
#         related_name='issued_parts'
#     )
#     part = models.ForeignKey('inventory.Part', on_delete=models.CASCADE)
#     source = models.CharField(
#         max_length=20, 
#         choices=SOURCE_CHOICES,
#         default='new',
#         help_text="Source from which part is issued"
#     )
#     quantity = models.PositiveIntegerField(default=1)
#     notes = models.TextField(blank=True, null=True)
#     issued_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.part} x {self.quantity} ({self.get_source_display()})"
# ========================= updated model with process complaint and resolution =========================
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

from clients.models import Client
from products.models import Product
from inventory.models import Part


# =========================
# Fault Master Table
# =========================
class Fault(models.Model):
    fault_name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.fault_name


# =========================
# Complaint
# =========================
class Complaint(models.Model):

    # 🔥 UPDATED: Added new statuses for resolution workflow
    STATUS_CHOICES = (
        ('new', 'New'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),        # ✅ NEW
        ('visit_only', 'Visit Only'),     # ✅ NEW
        ('cancel', 'Cancelled'),          # ✅ NEW
        ('closed', 'Closed'),
    )

    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    )

    complaint_no = models.CharField(max_length=20, unique=True, editable=False)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    fault = models.ForeignKey(
        Fault,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    other_details = models.TextField(blank=True, default='')

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new'
    )

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium'
    )

    # =========================
    # 🔥 NEW: Resolution Fields
    # =========================
    
    # Cost fields
    service_charge = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        validators=[MinValueValidator(0)],
        help_text="Engineer service charges"
    )
    
    total_parts_cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        validators=[MinValueValidator(0)],
        help_text="Total cost of parts used"
    )
    
    grand_total = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        validators=[MinValueValidator(0)],
        help_text="Service Charge + Parts Cost"
    )
    
    # Special case flags
    is_free = models.BooleanField(
        default=False, 
        help_text="Free service (no charges)"
    )
    
    is_amc = models.BooleanField(
        default=False, 
        help_text="Under Annual Maintenance Contract"
    )
    
    is_warranty = models.BooleanField(
        default=False, 
        help_text="Under Warranty"
    )
    
    # Resolution tracking
    resolved_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="When complaint was resolved"
    )
    
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='resolved_complaints',
        help_text="Engineer who resolved"
    )
    
    resolution_remarks = models.TextField(
        blank=True, 
        null=True,
        help_text="Remarks at time of resolution"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['complaint_no']),
            models.Index(fields=['resolved_at']),  # ✅ NEW index
        ]

    def save(self, *args, **kwargs):
        # Generate complaint number if not exists
        if not self.complaint_no:
            year = timezone.now().year
            last = Complaint.objects.filter(
                complaint_no__startswith=f"CMP-{year}"
            ).count() + 1
            self.complaint_no = f"CMP-{year}-{last:04d}"
        
        # 🔥 NEW: Auto-calculate grand_total
        if self.is_free or self.is_amc or self.is_warranty:
            # Special cases: No charges
            self.grand_total = 0
            self.service_charge = 0
            # Note: total_parts_cost is kept for record but not charged
        else:
            # Normal case: Service charge + parts cost
            self.grand_total = (self.service_charge or 0) + (self.total_parts_cost or 0)
        
        # Auto-set resolved_at if status is resolved
        if self.status == 'resolved' and not self.resolved_at:
            self.resolved_at = timezone.now()
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.complaint_no
    
    # =========================
    # 🔥 NEW: Helper Methods
    # =========================
    
    def can_be_resolved(self):
        """Check if complaint can be resolved"""
        return self.status in ['assigned', 'in_progress']
    
    def is_under_warranty_or_amc(self):
        """Check if complaint is under special coverage"""
        return self.is_free or self.is_amc or self.is_warranty
    
    def get_total_parts_used(self):
        """Get total quantity of parts used"""
        total = 0
        for assignment in self.assignments.filter(is_active=True):
            total += assignment.issued_parts.filter(
                usage_status='used'
            ).aggregate(total=models.Sum('used_quantity'))['total'] or 0
        return total
    
    def get_assigned_engineer(self):
        """Get currently assigned engineer"""
        active = self.assignments.filter(is_active=True).first()
        return active.engineer if active else None


# =========================
# Complaint Assignment
# =========================
class ComplaintAssignment(models.Model):
    complaint = models.ForeignKey(
        Complaint,
        on_delete=models.CASCADE,
        related_name='assignments'
    )

    engineer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'engineer'}
    )

    assigned_at = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=['complaint', 'engineer']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.complaint} → {self.engineer}"
    
    def get_issued_parts_summary(self):
        """Get summary of issued parts"""
        return self.issued_parts.all()


# =========================
# Parts Issue To Engineer
# =========================
class ComplaintPartIssue(models.Model):
    
    # 🔥 NEW: Usage status choices
    USAGE_STATUS = (
        ('issued', 'Issued'),           # Part issued but not yet used
        ('used', 'Used/Consumed'),       # Part used in service
        ('returned', 'Returned'),        # Part returned to inventory
        ('damaged', 'Damaged'),          # Part damaged
        ('lost', 'Lost'),                 # Part lost
    )
    
    SOURCE_CHOICES = (
        ('new', 'New'),
        ('used', 'Used'),
        ('outsource', 'Outsource'),
    )
    
    assignment = models.ForeignKey(
        ComplaintAssignment,
        on_delete=models.CASCADE,
        related_name='issued_parts'
    )
    part = models.ForeignKey('inventory.Part', on_delete=models.CASCADE)
    
    source = models.CharField(
        max_length=20, 
        choices=SOURCE_CHOICES,
        default='new',
        help_text="Source from which part is issued"
    )
    
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Quantity issued"
    )
    
    # =========================
    # 🔥 NEW: Resolution fields for parts
    # =========================
    
    used_quantity = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Quantity actually used in service"
    )
    
    part_cost_at_time = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        help_text="Part cost at resolution time (snapshot)"
    )
    
    usage_status = models.CharField(
        max_length=20, 
        choices=USAGE_STATUS, 
        default='issued',
        help_text="Current status of this part"
    )
    
    returned_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="When part was returned (if returned)"
    )
    
    notes = models.TextField(blank=True, null=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # 🔥 NEW

    class Meta:
        indexes = [
            models.Index(fields=['usage_status']),
            models.Index(fields=['part', 'usage_status']),
            models.Index(fields=['assignment', 'part']),
        ]

    def __str__(self):
        status_display = dict(self.USAGE_STATUS).get(self.usage_status, '')
        return f"{self.part} x {self.quantity} ({self.get_source_display()}) - {status_display}"
    
    # =========================
    # 🔥 NEW: Helper methods
    # =========================
    
    def calculate_cost(self):
        """Calculate cost for this part based on used quantity"""
        return self.used_quantity * self.part_cost_at_time
    
    def return_to_inventory(self):
        """Mark part as returned and update stock"""
        if self.usage_status == 'issued':
            self.usage_status = 'returned'
            self.returned_at = timezone.now()
            self.used_quantity = 0
            
            # Increase stock
            self.part.stock_quantity += self.quantity
            self.part.save()
            self.save()
            return True
        return False
    
    def can_be_used(self):
        """Check if part can be marked as used"""
        return self.usage_status == 'issued' and self.quantity > 0