from django.db import models


class GuestBook(models.Model):
    name       = models.CharField("Имя", max_length=100)
    email      = models.EmailField("Email", blank=True)
    message    = models.TextField("Сообщение")
    is_public  = models.BooleanField("Публичная запись", default=True)
    created_at = models.DateTimeField("Создано", auto_now_add=True)

    class Meta:
        verbose_name = "Запись в гостевой книге"
        verbose_name_plural = "Гостевая книга"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} — {self.created_at:%d.%m.%Y}"
