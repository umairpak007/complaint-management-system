from django.db import models


class Client(models.Model):
    name = models.CharField(max_length=200)
    primary_contact_no = models.CharField(max_length=20)
    alternate_contact_no = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    office_address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
