from django.urls import path
from . import views

app_name = 'rooms'

urlpatterns = [
    path('', views.rooms_home, name='rooms_home'),
    path('upcoming/', views.upcoming, name='upcoming'),
    path('price/', views.price, name='price'),
    path('my_karaoke/', views.my_karaoke, name='my_karaoke'),
    path('cabinet/', views.cabinet, name='cabinet'),
    path('reports/', views.reports, name='reports'),
    path('book/<int:slot_id>/', views.book_slot, name='book_slot'),
    path('payment/<int:booking_id>/', views.payment_page, name='payment_page'),
    path('cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('room/<slug:url_name>/', views.room_schedule, name='room_schedule'),
]