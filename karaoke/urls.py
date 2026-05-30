from django.urls import path
from django.contrib import admin
from django.urls import include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("admin/",              admin.site.urls),
    path("",                    views.rooms_home,     name="rooms_home"),
    path("accounts/",           include("django.contrib.auth.urls")),
    path("upcoming/",           views.upcoming,       name="upcoming"),
    path("price/",              views.price,          name="price"),
    path("my_karaoke/",         views.my_karaoke,     name="my_karaoke"),
    path("cabinet/",            views.cabinet,        name="cabinet"),
    path("reports/",            views.reports,        name="reports"),
    path("book/<int:slot_id>/", views.book_slot,      name="book_slot"),
    path("cancel/<int:booking_id>/", views.cancel_booking, name="cancel_booking"),
    path("room/<slug:url_name>/",    views.room_schedule,  name="room_schedule"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
