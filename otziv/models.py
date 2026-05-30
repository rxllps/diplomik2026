from django.db import models
from django.conf import settings


class Review(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    room = models.ForeignKey("rooms.Room", on_delete=models.CASCADE,
                             related_name="reviews", verbose_name="Комната")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name="reviews", verbose_name="Автор")
    rating = models.PositiveSmallIntegerField("Оценка", choices=RATING_CHOICES)
    text = models.TextField("Текст отзыва")
    is_approved = models.BooleanField("Одобрен", default=False)
    created_at = models.DateTimeField("Создано", auto_now_add=True)

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ["-created_at"]
        # Один пользователь — один отзыв на комнату
        unique_together = ("room", "user")

    def __str__(self):
        return f"{self.user} → {self.room} [{self.rating}★]"
