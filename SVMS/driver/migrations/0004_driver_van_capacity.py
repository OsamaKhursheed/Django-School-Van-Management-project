# Generated by Django 4.2.5 on 2023-09-29 16:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('driver', '0003_driver_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='driver',
            name='van_capacity',
            field=models.IntegerField(default=0),
        ),
    ]
