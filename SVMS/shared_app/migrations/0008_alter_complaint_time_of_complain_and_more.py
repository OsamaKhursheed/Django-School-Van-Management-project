# Generated by Django 4.2.5 on 2023-09-21 17:11

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('shared_app', '0007_alter_fee_inc_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='complaint',
            name='time_of_complain',
            field=models.TimeField(default=django.utils.timezone.now, null=True),
        ),
        migrations.AlterField(
            model_name='delay_req',
            name='time_of_complain',
            field=models.TimeField(default=django.utils.timezone.now, null=True),
        ),
        migrations.AlterField(
            model_name='fee_inc',
            name='time_of_complain',
            field=models.TimeField(default=django.utils.timezone.now, null=True),
        ),
    ]
