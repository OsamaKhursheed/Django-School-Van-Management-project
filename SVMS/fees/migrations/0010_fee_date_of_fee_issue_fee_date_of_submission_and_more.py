# Generated by Django 4.2.5 on 2023-09-26 14:42

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('fees', '0009_remove_fee_date_of_fee_issue_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='fee',
            name='date_of_fee_issue',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='fee',
            name='date_of_submission',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='fee',
            name='due_date_of_fee',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='fee',
            name='fee_amount',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='fee',
            name='month_of_fee',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='fee',
            name='status',
            field=models.CharField(default='Pending', max_length=20),
        ),
    ]