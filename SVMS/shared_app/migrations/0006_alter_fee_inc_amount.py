# Generated by Django 4.1.7 on 2023-09-20 17:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shared_app', '0005_alter_complaint_owner_approval_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fee_inc',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]
