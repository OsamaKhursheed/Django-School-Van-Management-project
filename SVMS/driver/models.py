from django.db import models

# Create your models here.
class Driver(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    profile_image = models.ImageField(upload_to='driver_profiles/', null=True, blank=True)
    father_name = models.CharField(max_length=255)
    address = models.TextField()
    area = models.CharField(max_length=255)
    cnic = models.CharField(max_length=15)
    van = models.CharField(max_length=20)
    van_capacity=models.IntegerField(default=0)
    email = models.EmailField()
    username = models.CharField(max_length=100, unique=True)
    phone_no = models.CharField(max_length=20)
    password = models.CharField(max_length=100)
    status= models.BooleanField(default=False)
    fee_amount=models.IntegerField(default=1500)
    
