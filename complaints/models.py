# from django.db import models
# from django.utils import timezone
# from django.conf import settings
#
# from clients.models import Client
# from products.models import Product
#
#
# # =========================
# # Fault Master Table
# # =========================
# class Fault(models.Model):
#     fault_name = models.CharField(max_length=100, unique=True)
#     description = models.TextField(blank=True, null=True)
#     is_active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return self.fault_name
#
#
#
#
#
# # =========================
# # Complaint
# # =========================
# class Complaint(models.Model):
#
#     STATUS_CHOICES = (
#         ('new', 'New'),
#         ('assigned', 'Assigned'),
#         ('in_progress', 'In Progress'),
#         ('closed', 'Closed'),
#     )
#
#     PRIORITY_CHOICES = (
#         ('low', 'Low'),
#         ('medium', 'Medium'),
#         ('high', 'High'),
#     )
#
#     complaint_no = models.CharField(max_length=20, unique=True, editable=False)
#     client = models.ForeignKey(Client, on_delete=models.CASCADE)
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#
#     fault = models.ForeignKey(
#         Fault,
#         on_delete=models.PROTECT,
#         null=True,
#         blank=True
#
#     )
#     # dropdown fault (from Fault table)
#     fault = models.ForeignKey(Fault, on_delete=models.PROTECT)
#
#     other_details = models.TextField(blank=True, default='Service Only')
#
#     status = models.CharField(
#         max_length=20,
#         choices=STATUS_CHOICES,
#         default='new'
#     )
#
#     priority = models.CharField(
#         max_length=20,
#         choices=PRIORITY_CHOICES,
#         default='medium'
#     )
#
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     def save(self, *args, **kwargs):
#         if not self.complaint_no:
#             year = timezone.now().year
#             last = Complaint.objects.filter(
#                 complaint_no__startswith=f"CMP-{year}"
#             ).count() + 1
#             self.complaint_no = f"CMP-{year}-{last:04d}"
#         super().save(*args, **kwargs)
#
#     def __str__(self):
#         return self.complaint_no
#
#
# # =========================
# # Complaint Assignment
# # =========================
# class ComplaintAssignment(models.Model):
#     complaint = models.ForeignKey(
#         Complaint,
#         on_delete=models.CASCADE,
#         related_name='assignments'
#     )
#
#     engineer = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         limit_choices_to={'role': 'engineer'}
#     )
#
#     assigned_at = models.DateTimeField(auto_now_add=True)
#     remarks = models.TextField(blank=True, null=True)
#     is_active = models.BooleanField(default=True)
#
#     def __str__(self):
#         return f"{self.complaint} → {self.engineer}"
#==================================================================================deep seek
from django.db import models
from django.utils import timezone
from django.conf import settings

from clients.models import Client
from products.models import Product


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

    STATUS_CHOICES = (
        ('new', 'New'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
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

    # Fixed: Only one fault field defined
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

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.complaint_no:
            year = timezone.now().year
            last = Complaint.objects.filter(
                complaint_no__startswith=f"CMP-{year}"
            ).count() + 1
            self.complaint_no = f"CMP-{year}-{last:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.complaint_no


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

    def __str__(self):
        return f"{self.complaint} → {self.engineer}"