# Generated by Django 4.1.7 on 2023-09-26 14:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fees', '0008_remove_fee_owner_profit'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fee',
            name='date_of_fee_issue',
        ),
        migrations.RemoveField(
            model_name='fee',
            name='date_of_submission',
        ),
        migrations.RemoveField(
            model_name='fee',
            name='due_date_of_fee',
        ),
        migrations.RemoveField(
            model_name='fee',
            name='fee_amount',
        ),
        migrations.RemoveField(
            model_name='fee',
            name='month_of_fee',
        ),
        migrations.RemoveField(
            model_name='fee',
            name='status',
        ),
    ]
