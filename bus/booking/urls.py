from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('book/<int:bus_id>/', views.book_ticket, name='book_ticket'),
    path('cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('history/', views.BookingHistoryView.as_view(), name='booking_history'),
]
