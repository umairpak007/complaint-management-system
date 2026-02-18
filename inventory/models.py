from django.db import models

class Part(models.Model):
    name = models.CharField(max_length=100)
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    # dummy_field = models.CharField(max_length=10, null=True, blank=True)
    
    SOURCE_CHOICES = (
        ('new', 'New'),
        ('used', 'Used'),
        ('outsource', 'Outsource'),
    )
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='')
    
    stock_quantity = models.IntegerField(default=0, help_text="Available stock quantity")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} | {self.make} | {self.model} | {self.source}"

