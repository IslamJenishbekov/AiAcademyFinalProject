from django.db import models


class Client(models.Model):
    full_name = models.CharField(max_length=255, verbose_name="ФИО")
    inn = models.CharField(max_length=12, unique=True, verbose_name="ИНН")  # Добавляем ИНН, делаем его уникальным
    age = models.IntegerField(verbose_name="Возраст")
    monthly_income = models.FloatField(verbose_name="Ежемесячный доход")
    debt_ratio = models.FloatField(verbose_name="Коэффициент долговой нагрузки")
    utilization = models.FloatField(verbose_name="Процент использования кредита")
    num_30_59_days_past_due = models.IntegerField(verbose_name="Количество просрочек (30-59 дней)")
    num_credit_lines_loans = models.IntegerField(verbose_name="Количество кредитных линий/займов")

    # Добавляем поля даты
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата последнего обновления")

    def __str__(self):
        return f"{self.full_name} (ИНН: {self.inn})"

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"