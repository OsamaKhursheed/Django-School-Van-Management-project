from django.db import models
from driver.models import Driver

class Student(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    profile_image = models.ImageField(upload_to='student_profiles/', null=True, blank=True)
    father_name = models.CharField(max_length=255)
    address = models.TextField()
    area = models.CharField(max_length=255)
    roll_no = models.CharField(max_length=20)
    grade = models.CharField(max_length=10)
    email = models.EmailField()
    username = models.CharField(max_length=100, unique=True)
    phone_no = models.CharField(max_length=20)
    password = models.CharField(max_length=100)
    driver_id = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True, default=None)
    status= models.BooleanField(default=False)