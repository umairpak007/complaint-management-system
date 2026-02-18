#this is forms.py file for complaints app
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Complaint, ComplaintPartIssue
from inventory.models import Part

class ComplaintResolutionForm(forms.ModelForm):
    """
    Form for engineers to resolve complaints
    """
    class Meta:
        model = Complaint
        fields = [
            'service_charge',
            'is_free',
            'is_amc',
            'is_warranty',
            'resolution_remarks',
        ]
        widgets = {
            'service_charge': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'id': 'service-charge'
            }),
            'resolution_remarks': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter resolution details...'
            }),
            'is_free': forms.CheckboxInput(attrs={
                'class': 'special-case-checkbox',
                'id': 'is-free'
            }),
            'is_amc': forms.CheckboxInput(attrs={
                'class': 'special-case-checkbox',
                'id': 'is-amc'
            }),
            'is_warranty': forms.CheckboxInput(attrs={
                'class': 'special-case-checkbox',
                'id': 'is-warranty'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.complaint = kwargs.pop('complaint', None)
        super().__init__(*args, **kwargs)
        
        # Disable fields if complaint already resolved
        if self.complaint and self.complaint.status == 'resolved':
            for field in self.fields:
                self.fields[field].disabled = True

    def clean(self):
        cleaned_data = super().clean()
        is_free = cleaned_data.get('is_free')
        is_amc = cleaned_data.get('is_amc')
        is_warranty = cleaned_data.get('is_warranty')
        service_charge = cleaned_data.get('service_charge')

        # Validation: Only one special case can be selected
        special_cases = sum([is_free, is_amc, is_warranty])
        if special_cases > 1:
            raise ValidationError("Select only one: Free, AMC, or Warranty")

        # Validation: Service charge should be 0 for special cases
        if special_cases > 0 and service_charge and service_charge > 0:
            raise ValidationError(
                "Service charge must be 0 for Free/AMC/Warranty services"
            )

        return cleaned_data


class PartUsageForm(forms.Form):
    """
    Form for each part used in resolution
    """
    part_id = forms.IntegerField(widget=forms.HiddenInput())
    part_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'})
    )
    available_quantity = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'readonly': 'readonly', 'class': 'form-control'})
    )
    used_quantity = forms.IntegerField(
        min_value=0,
        initial=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control used-quantity',
            'min': '0',
            'step': '1'
        })
    )
    part_cost = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'readonly': 'readonly',
            'class': 'form-control part-cost'
        })
    )
    total_cost = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'readonly': 'readonly',
            'class': 'form-control part-total'
        })
    )

    def __init__(self, *args, **kwargs):
        self.part = kwargs.pop('part', None)
        super().__init__(*args, **kwargs)
        
        if self.part:
            self.fields['part_id'].initial = self.part.id
            self.fields['part_name'].initial = str(self.part)
            self.fields['available_quantity'].initial = self.part.stock_quantity
            self.fields['part_cost'].initial = float(self.part.selling_price or 0)

    def clean_used_quantity(self):
        used_qty = self.cleaned_data.get('used_quantity')
        available = self.cleaned_data.get('available_quantity') or 0
        
        if used_qty and used_qty > available:
            raise ValidationError(
                f"Only {available} units available in stock"
            )
        return used_qty


class PartUsageFormSet(forms.BaseFormSet):
    """
    FormSet to handle multiple parts
    """
    def __init__(self, *args, **kwargs):
        self.complaint = kwargs.pop('complaint', None)
        super().__init__(*args, **kwargs)

    def get_part_issues(self):
        """Get all issued parts for this complaint"""
        if not self.complaint:
            return []
        
        return ComplaintPartIssue.objects.filter(
            assignment__complaint=self.complaint,
            assignment__is_active=True
        ).select_related('part')

    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        if hasattr(self, 'part_issues') and index < len(self.part_issues):
            kwargs['part'] = self.part_issues[index].part
        return kwargs

    def total_parts_cost(self):
        """Calculate total cost of all used parts"""
        total = 0
        if self.is_valid():
            for form in self.forms:
                used_qty = form.cleaned_data.get('used_quantity', 0)
                part_cost = form.cleaned_data.get('part_cost', 0)
                total += (used_qty or 0) * (part_cost or 0)
        return total


def part_usage_formset_factory(complaint=None):
    """Create a formset for part usage"""
    formset = forms.formset_factory(
        PartUsageForm,
        formset=PartUsageFormSet,
        extra=0,  # No extra forms, only existing parts
        can_delete=False
    )
    
    if complaint:
        # Get issued parts for this complaint
        part_issues = ComplaintPartIssue.objects.filter(
            assignment__complaint=complaint,
            assignment__is_active=True
        ).select_related('part')
        
        # Create initial data
        initial = []
        for issue in part_issues:
            initial.append({
                'part_id': issue.part.id,
                'used_quantity': 0,  # Default to 0
            })
        
        # ✅ FIXED: Properly create formset with initial data
        formset = formset(initial=initial)
        formset.complaint = complaint
        formset.part_issues = list(part_issues)
        
        # ✅ FIXED: Set part for each form
        for i, form in enumerate(formset.forms):
            if i < len(part_issues):
                form.part = part_issues[i].part
    
    return formset


class ComplaintStatusUpdateForm(forms.ModelForm):
    """
    Simple form for status updates (visit_only, cancel)
    """
    class Meta:
        model = Complaint
        fields = ['status', 'resolution_remarks']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'resolution_remarks': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Reason for status update...'
            }),
        }

    def clean_status(self):
        status = self.cleaned_data.get('status')
        if status not in ['visit_only', 'cancel']:
            raise ValidationError("Invalid status for this form")
        return status