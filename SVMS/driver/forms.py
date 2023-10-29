from django import forms
from .models import Driver

class DriverRegistrationForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = '__all__'

class DriverUpdateForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = ['first_name','last_name','profile_image','father_name','address','cnic','van','van_capacity','email','username','phone_no','password']