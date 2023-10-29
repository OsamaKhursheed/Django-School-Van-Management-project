from django import forms
from .models import Student

class StudentRegistrationForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = '__all__'  # Include all fields from the Student model

class StudentUpdateForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'profile_image', 'father_name', 'address', 'roll_no', 'grade', 'email', 'username', 'phone_no', 'password']
