
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import datetime


class Room(models.Model):
    name = models.CharField("Название", max_length=100)
    url_name = models.SlugField("URL-имя", unique=True)
    capacity = models.PositiveIntegerField("Вместимость", default=10)
    description = models.TextField("Описание", blank=True)
    photo = models.ImageField("Фото", upload_to="rooms/", blank=True, null=True)
    is_active = models.BooleanField("Активна", default=True)
    price_per_hour = models.DecimalField("Цена/час", max_digits=8, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Комната"
        verbose_name_plural = "Комнаты"

    def __str__(self):
        return self.name


class ServicePackage(models.Model):
    name        = models.CharField("Пакет", max_length=100)
    description = models.TextField("Описание", blank=True)
    price       = models.DecimalField("Цена", max_digits=8, decimal_places=2)
    duration_hours = models.PositiveIntegerField("Длительность (ч)", default=2)
    max_guests  = models.PositiveIntegerField("Макс. гостей", default=10)
    includes_food = models.BooleanField("Включает еду", default=False)
    is_active   = models.BooleanField("Активен", default=True)

    class Meta:
        verbose_name = "Пакет услуг"
        verbose_name_plural = "Пакеты услуг"

    def __str__(self):
        return f"{self.name} — {self.price} руб."


class TimeSlot(models.Model):
    room       = models.ForeignKey(Room, on_delete=models.CASCADE,
                                   related_name="slots", verbose_name="Комната")
    date       = models.DateField("Дата")
    start_time = models.TimeField("Начало")
    end_time   = models.TimeField("Конец")
    is_booked  = models.BooleanField("Занят", default=False)

    class Meta:
        verbose_name = "Слот"
        verbose_name_plural = "Слоты"
        unique_together = ("room", "date", "start_time")
        ordering = ["date", "start_time"]

    def __str__(self):
        return f"{self.room} | {self.date} {self.start_time}–{self.end_time}"


class Booking(models.Model):
    STATUS_CHOICES = [
        ("pending",   "Ожидает оплаты"),
        ("confirmed", "Подтверждено"),
        ("cancelled", "Отменено"),
        ("completed", "Завершено"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                   related_name="bookings", verbose_name="Пользователь")
    slot = models.OneToOneField(TimeSlot, on_delete=models.CASCADE,
                                      related_name="booking", verbose_name="Слот")
    package = models.ForeignKey(ServicePackage, on_delete=models.SET_NULL,
                                   null=True, blank=True, verbose_name="Пакет")
    guests = models.PositiveIntegerField("Кол-во гостей", default=1)
    comment = models.TextField("Комментарий", blank=True)
    status = models.CharField("Статус", max_length=20,
                                  choices=STATUS_CHOICES, default="pending")
    total_price = models.DecimalField("Итого", max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"
        ordering = ["-created_at"]

    def __str__(self):
        return f"#{self.pk} {self.user} → {self.slot}"

    def save(self, *args, **kwargs):
        # Автоматически считаем итоговую цену
        if self.package:
            self.total_price = self.package.price
        else:
            slot = self.slot
            room = slot.room
            dt_start = datetime.combine(slot.date, slot.start_time)
            dt_end   = datetime.combine(slot.date, slot.end_time)
            hours = (dt_end - dt_start).seconds / 3600
            self.total_price = float(room.price_per_hour) * hours
        super().save(*args, **kwargs)


class Payment(models.Model):
    METHOD_CHOICES = [
        ("cash",   "Наличные"),
        ("card",   "Карта"),
        ("online", "Онлайн"),
    ]
    STATUS_CHOICES = [
        ("pending",  "Ожидает"),
        ("paid",     "Оплачено"),
        ("refunded", "Возврат"),
        ("failed",   "Ошибка"),
    ]

    booking    = models.OneToOneField(Booking, on_delete=models.CASCADE,
                                      related_name="payment", verbose_name="Бронирование")
    amount     = models.DecimalField("Сумма", max_digits=10, decimal_places=2)
    method     = models.CharField("Способ", max_length=20,
                                  choices=METHOD_CHOICES, default="online")
    status     = models.CharField("Статус", max_length=20,
                                  choices=STATUS_CHOICES, default="pending")
    paid_at    = models.DateTimeField("Оплачено", null=True, blank=True)
    created_at = models.DateTimeField("Создано", auto_now_add=True)

    class Meta:
        verbose_name = "Платёж"
        verbose_name_plural = "Платежи"

    def __str__(self):
        return f"Платёж #{self.pk} — {self.amount} руб. [{self.status}]"

    def mark_paid(self):
        self.status  = "paid"
        self.paid_at = timezone.now()
        self.save()
        self.booking.status = "confirmed"
        self.booking.slot.is_booked = True
        self.booking.slot.save()
        self.booking.save()
