from django import forms
from .models import Complaint ,fee_inc,delay_req

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['complain_content']
        widgets = {
            'complain_content': forms.Textarea(attrs={'rows': 4}),
        }

    # Add the following line to make the field required
    complain_content = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=True)

class FeeIncreaseRequestForm(forms.ModelForm):
    class Meta:
        model = fee_inc  # Associate the form with the fee_inc model
        fields = ['reason', 'amount']  

class delayRequestForm(forms.ModelForm):
    class Meta:
        model = delay_req  # Associate the form with the fee_inc model
        fields = ['reason', 'time','date']  