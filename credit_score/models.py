from django.db import models
from django.utils import timezone


class Client(models.Model):

    full_name = models.CharField(max_length=255, verbose_name="ФИО")
    age = models.IntegerField(verbose_name="Возраст")
    inn = models.CharField(max_length=12, unique=True, verbose_name="ИНН")


    created_at = models.DateTimeField(default=timezone.now, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата последнего обновления")


    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"
        ordering = ['full_name']


    def __str__(self):
        return f"{self.full_name} (ИНН: {self.inn})"