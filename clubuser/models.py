
from django.db import models
from django.contrib.auth.models import AbstractUser


class ClubUser(AbstractUser):
    phone = models.CharField("Телефон", max_length=20, blank=True)
    birth_date = models.DateField("Дата рождения", null=True, blank=True)
    avatar = models.ImageField("Аватар", upload_to="avatars/", blank=True, null=True)
    bonus_points = models.PositiveIntegerField("Бонусные баллы", default=0)
    is_vip = models.BooleanField("VIP", default=False)

    class Meta:
        verbose_name = "Пользователь клуба"
        verbose_name_plural = "Пользователи клуба"

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.phone})"

    def add_bonus(self, amount):
        self.bonus_points += int(amount * 0.05)  # 5% от суммы заказа
        self.save()
