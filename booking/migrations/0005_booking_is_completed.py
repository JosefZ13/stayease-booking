# Generated by Django 5.2 on 2025-04-17 10:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0004_booking_guests'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='is_completed',
            field=models.BooleanField(default=False),
        ),
    ]
