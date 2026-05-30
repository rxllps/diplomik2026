
# ── rooms/forms.py ─────────────────────────────────────────────────────────────
from django import forms
from .models import Booking, ServicePackage


PAYMENT_METHODS = [
    ("online", "Онлайн"),
    ("card",   "Карта при посещении"),
    ("cash",   "Наличные"),
]

class BookingForm(forms.ModelForm):
    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHODS, label="Способ оплаты",
        widget=forms.RadioSelect
    )

    class Meta:
        model  = Booking
        fields = ["package", "guests", "comment"]
        widgets = {
            "comment": forms.Textarea(attrs={"rows": 3}),
        }
        labels = {
            "package": "Пакет услуг (необязательно)",
            "guests":  "Количество гостей",
            "comment": "Пожелания",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["package"].queryset = ServicePackage.objects.filter(is_active=True)
        self.fields["package"].required = False


# ── rooms/urls.py ──────────────────────────────────────────────────────────────
# from django.urls import path
# from . import views
# 
# urlpatterns = [
#     path("",                    views.rooms_home,     name="rooms_home"),
#     path("upcoming/",           views.upcoming,       name="upcoming"),
#     path("price/",              views.price,          name="price"),
#     path("my_karaoke/",         views.my_karaoke,     name="my_karaoke"),
#     path("cabinet/",            views.cabinet,        name="cabinet"),
#     path("reports/",            views.reports,        name="reports"),
#     path("book/<int:slot_id>/", views.book_slot,      name="book_slot"),
#     path("cancel/<int:booking_id>/", views.cancel_booking, name="cancel_booking"),
#     path("room/<slug:url_name>/",    views.room_schedule,  name="room_schedule"),
# ]


# ── untitled/urls.py ───────────────────────────────────────────────────────────
# from django.contrib import admin
# from django.urls import path, include
# from django.conf import settings
# from django.conf.urls.static import static
# 
# urlpatterns = [
#     path("admin/", admin.site.urls),
#     path("",       include("rooms.urls")),
#     path("accounts/", include("django.contrib.auth.urls")),
# ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
