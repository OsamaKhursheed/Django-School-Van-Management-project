from django.db import models
from django.conf import settings
from student.models import Student
from driver.models import Driver
from django.utils import timezone

class Complaint(models.Model):
    student_id = models.ForeignKey(Student, on_delete=models.CASCADE)
    driver_id = models.PositiveIntegerField()
    complain_content = models.TextField()
    time_of_complain = models.TimeField(default=timezone.now, null=True)
    day_of_complain = models.DateField(default=timezone.now)
    owner_approval = models.CharField(max_length=7,default='Pending')
    owner_comments = models.TextField(default='-')

class fee_inc(models.Model):
    Driver_id = models.ForeignKey(Driver, on_delete=models.CASCADE)
    reason = models.TextField()
    amount = models.IntegerField()
    time_of_complain = models.TimeField(default=timezone.now, null=True)
    day_of_complain = models.DateField(default=timezone.now)
    owner_approval = models.CharField(max_length=7,default='Pending')
    owner_comments = models.TextField(default='-')

class delay_req(models.Model):
    Driver_id = models.ForeignKey(Driver, on_delete=models.CASCADE)
    reason = models.TextField()
    time = models.TimeField()
    date = models.DateField()
    time_of_complain = models.TimeField(default=timezone.now, null=True)
    day_of_complain = models.DateField(default=timezone.now)
    owner_approval = models.CharField(max_length=7,default='Pending')
    owner_comments = models.TextField(default='-')