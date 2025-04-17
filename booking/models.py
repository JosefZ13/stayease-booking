from django.db import models
from django.core.exceptions import ValidationError
from datetime import timedelta, date
from django.db.models.signals import post_delete
from django.dispatch import receiver

class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.name

class Room(models.Model):
    room_number = models.CharField(max_length=10, unique=True)
    room_type = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    is_available = models.BooleanField(default=True)
    capacity = models.IntegerField(default=2)

    def __str__(self):
        return f"Room {self.room_number} ({self.room_type})"

class Booking(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    total_price = models.DecimalField(max_digits=8, decimal_places=2)
    guests = models.PositiveIntegerField(default=1)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        overlapping = Booking.objects.filter(
            room=self.room,
            check_in_date__lt=self.check_out_date,
            check_out_date__gt=self.check_in_date
        ).exclude(id=self.id)
        if overlapping.exists():
            raise ValidationError("Det finns redan en bokning för detta rum under valt datumintervall.")

        if self.guests > self.room.capacity:
            raise ValidationError("Antalet gäster överskrider rummets kapacitet.")

    def save(self, *args, **kwargs):
        self.full_clean()
        num_nights = (self.check_out_date - self.check_in_date).days
        self.total_price = num_nights * self.room.price

        if self.check_out_date < date.today():
            self.is_completed = True

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.customer.name} booked {self.room.room_number}"

# Automatisk rensning av kunder utan bokningar
@receiver(post_delete, sender=Booking)
def delete_customer_if_no_bookings_left(sender, instance, **kwargs):
    customer = instance.customer
    if not Booking.objects.filter(customer=customer).exists():
        customer.delete()
