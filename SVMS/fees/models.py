from django.conf import settings
from student.models import Student
from driver.models import Driver
from django.utils import timezone
from datetime import timedelta
from django.db import models

class Fee(models.Model):
    student_id = models.ForeignKey(Student, on_delete=models.CASCADE)
    driver_id = models.ForeignKey(Driver, on_delete=models.CASCADE)
    fee_amount = models.IntegerField(default=0)
    month_of_fee = models.DateField(null=True)
    date_of_fee_issue = models.DateField(default=timezone.now)
    due_date_of_fee = models.DateField(null=True)
    status = models.CharField(default='Pending', max_length=20)
    date_of_submission = models.DateField(null=True)
    Owner_fee =models.IntegerField(default=0)



    def save(self, *args, **kwargs):
        if not self.pk:  # Check if this is a new Fee object (not an update)
            self.due_date_of_fee = self.date_of_fee_issue + timedelta(days=10)  # Calculate due date
            if self.date_of_submission and self.date_of_submission > self.due_date_of_fee:
                self.fee_amount += 500  # Add 500 to the fee amount if submitted after due date
        super(Fee, self).save(*args, **kwargs)