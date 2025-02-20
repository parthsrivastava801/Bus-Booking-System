from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import ListView
from django.db.models import Q
from .models import Bus, Booking, User
from datetime import datetime, timedelta

@login_required
def home(request):
    if request.method == 'POST':
        source = request.POST.get('source')
        destination = request.POST.get('destination')
        date = request.POST.get('date')
        
        buses = Bus.objects.filter(
            source=source,
            destination=destination,
            is_active=True,
            available_seats__gt=0
        ).order_by('departure_time')
        
        return render(request, 'booking/search_results.html', {'buses': buses})
    return render(request, 'booking/home.html')

@login_required
def book_ticket(request, bus_id):
    bus = Bus.objects.get(id=bus_id)
    if request.method == 'POST':
        passengers = request.POST.getlist('passenger_name[]')
        ages = request.POST.getlist('passenger_age[]')
        
        total_fare = bus.fare * len(passengers)
        
        if request.user.wallet_balance < total_fare:
            return render(request, 'booking/error.html', 
                        {'message': 'Insufficient wallet balance'})
        
        booking = Booking.objects.create(
            user=request.user,
            bus=bus,
            travel_date=request.POST.get('travel_date'),
            total_fare=total_fare
        )
        
        for i, (name, age) in enumerate(zip(passengers, ages)):
            Passenger.objects.create(
                booking=booking,
                name=name,
                age=age,
                seat_number=bus.available_seats - i
            )
        
        bus.available_seats -= len(passengers)
        bus.save()
        
        request.user.wallet_balance -= total_fare
        request.user.save()
        
        return redirect('booking_history')
    
    return render(request, 'booking/book_ticket.html', {'bus': bus})

@login_required
def cancel_booking(request, booking_id):
    booking = Booking.objects.get(id=booking_id)
    
    if booking.user != request.user:
        return redirect('booking_history')
    
    time_until_departure = booking.travel_date - timezone.now().date()
    if time_until_departure < timedelta(hours=6):
        return render(request, 'booking/error.html',
                    {'message': 'Cannot cancel within 6 hours of departure'})
    
    booking.status = 'CANCELLED'
    booking.save()
    
    # Refund the user
    request.user.wallet_balance += booking.total_fare
    request.user.save()
    
    # Restore bus seats
    bus = booking.bus
    bus.available_seats += booking.passengers.count()
    bus.save()
    
    return redirect('booking_history')

class BookingHistoryView(ListView):
    model = Booking
    template_name = 'booking/booking_history.html'
    context_object_name = 'bookings'
    
    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).order_by('-booking_date')
