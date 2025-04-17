from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db.models import Sum
from .models import Room, Customer, Booking
from datetime import datetime

# Home - Visa alla tillgängliga rum
def home(request):
    rooms = Room.objects.filter(is_available=True)
    return render(request, 'booking/home.html', {'rooms': rooms})

# Booking - Visa bokningssidan med alla tillgängliga rum
def booking(request):
    rooms = Room.objects.filter(is_available=True)
    return render(request, 'booking/booking.html', {'rooms': rooms})

# Booking form - Visa bokningsformuläret för ett valt rum
def booking_form(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    return render(request, 'booking/booking_form.html', {'room': room})

def submit_booking(request):
    """
    Process the booking form submission.
    """
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        room_id = request.POST.get('room_id')
        check_in = request.POST.get('check_in_date')
        check_out = request.POST.get('check_out_date')

        # Hantera gästantal robust
        try:
            guests = int(request.POST.get('guests') or 1)
        except ValueError:
            guests = 1

        # Validera namn & e-post
        if not name or not email:
            return HttpResponse("Namn och e-post krävs.", status=400)

        # Hämta rum
        room = get_object_or_404(Room, id=room_id)

        # Hämta eller skapa kund
        customer, created = Customer.objects.get_or_create(email=email)
        if created or not customer.name:
            customer.name = name
            customer.save()

        # Beräkna totalpris
        nights = (datetime.strptime(check_out, "%Y-%m-%d") - datetime.strptime(check_in, "%Y-%m-%d")).days
        total_price = room.price * nights

        # Skapa bokning
        booking = Booking.objects.create(
            customer=customer,
            room=room,
            check_in_date=check_in,
            check_out_date=check_out,
            total_price=total_price,
            guests=guests
        )

        # Markera rummet som otillgängligt
        room.is_available = False
        room.save()

        return redirect('booking_confirmation', booking_id=booking.id)

    return redirect('home')

# Booking confirmation
def booking_confirmation(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, 'booking/confirmation.html', {'booking': booking})

# Gallery
def gallery(request):
    return render(request, 'booking/gallery.html')

# Admin dashboard
def admin_dashboard(request):
    bookings = Booking.objects.all()
    income = bookings.aggregate(Sum('total_price'))['total_price__sum'] or 0
    return render(request, 'booking/admin_dashboard.html', {
        'bookings': bookings,
        'income': income
    })

# Edit booking
def edit_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if request.method == 'POST':
        booking.check_in_date = request.POST.get('check_in_date')
        booking.check_out_date = request.POST.get('check_out_date')
        booking.total_price = request.POST.get('total_price')
        booking.save()
        return redirect('admin_dashboard')

    return render(request, 'booking/edit_booking.html', {'booking': booking})

# Delete booking
def delete_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.delete()
    return redirect('admin_dashboard')

# Room search
def room_search(request):
    rooms = Room.objects.filter(is_available=True)

    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')
    guests = request.GET.get('guests')
    room_type = request.GET.get('room_type')
    capacity = request.GET.get('capacity')
    max_price = request.GET.get('max_price')

    try:
        guests = int(guests) if guests else None
    except ValueError:
        guests = None

    try:
        capacity = int(capacity) if capacity else None
    except ValueError:
        capacity = None

    try:
        max_price = float(max_price) if max_price else None
    except ValueError:
        max_price = None

    if room_type:
        rooms = rooms.filter(room_type__icontains=room_type)
    if capacity:
        rooms = rooms.filter(capacity__gte=capacity)
    if max_price:
        rooms = rooms.filter(price__lte=max_price)

    if check_in and check_out:
        try:
            check_in_date = datetime.strptime(check_in, "%Y-%m-%d").date()
            check_out_date = datetime.strptime(check_out, "%Y-%m-%d").date()
            if check_in_date < check_out_date:
                rooms = rooms.exclude(
                    booking__check_in_date__lt=check_out_date,
                    booking__check_out_date__gt=check_in_date
                )
        except ValueError:
            pass

    if guests:
        rooms = rooms.filter(capacity__gte=guests)

    return render(request, 'booking/room_search.html', {'rooms': rooms})
