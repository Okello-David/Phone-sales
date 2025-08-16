from django import forms
from django.forms import inlineformset_factory
from .models import Assignment, AssignedPhone

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['agent', 'remarks', 'previous_assignment']
        widgets = {
            'remarks': forms.Textarea(attrs={'rows': 2}),
        }

AssignedPhoneFormSet = inlineformset_factory(
    Assignment,
    AssignedPhone,
    fields=('phone', 'quantity_given'),
    extra=1,
    can_delete=True
)

# NEW: Form for partial reassignment
class ReassignPhoneForm(forms.Form):
    phone_id = forms.IntegerField(widget=forms.HiddenInput())
    phone_name = forms.CharField(disabled=True, required=False, label="Phone")
    quantity_available = forms.IntegerField(disabled=True, required=False, label="Available")
    quantity_to_move = forms.IntegerField(min_value=0, required=False, label="Qty to Move")
    move = forms.BooleanField(required=False, label="Move?")

