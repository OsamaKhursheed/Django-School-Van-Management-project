# Generated by Django 4.2.5 on 2023-09-18 13:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('driver', '0002_driver_fee_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='driver',
            name='status',
            field=models.BooleanField(default=False),
        ),
    ]
