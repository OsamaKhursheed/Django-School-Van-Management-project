# Generated by Django 4.2.5 on 2023-09-06 15:25

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Driver',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('profile_image', models.ImageField(blank=True, null=True, upload_to='driver_profiles/')),
                ('father_name', models.CharField(max_length=255)),
                ('address', models.TextField()),
                ('area', models.CharField(max_length=255)),
                ('cnic', models.CharField(max_length=15)),
                ('van', models.CharField(max_length=20)),
                ('email', models.EmailField(max_length=254)),
                ('username', models.CharField(max_length=100, unique=True)),
                ('phone_no', models.CharField(max_length=20)),
                ('password', models.CharField(max_length=100)),
            ],
        ),
    ]
