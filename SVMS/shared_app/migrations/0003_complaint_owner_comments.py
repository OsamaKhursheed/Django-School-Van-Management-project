# Generated by Django 4.1.7 on 2023-09-16 16:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shared_app', '0002_alter_complaint_driver_id_alter_complaint_student_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='complaint',
            name='owner_comments',
            field=models.TextField(default='-'),
        ),
    ]