from django.db import models


class Product(models.Model):
    brand_make = models.CharField(max_length=100)
    brand_model = models.CharField(max_length=100)
    product_type = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.brand_make} - {self.brand_model}"
