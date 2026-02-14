from django.contrib import admin
from .models import Complaint,Fault
from products.models import Product

admin.site.register(Complaint)
admin.site.register(Fault)

