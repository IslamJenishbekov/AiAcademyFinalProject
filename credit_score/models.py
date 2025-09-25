from django.db import models
from django.utils import timezone


class Client(models.Model):

    full_name = models.CharField(max_length=255, verbose_name="ФИО")
    age = models.IntegerField(verbose_name="Возраст")
    inn = models.CharField(max_length=12, unique=True, verbose_name="ИНН")

    # Добавляем поля, необходимые для модели машинного обучения
    utilization = models.FloatField(
        verbose_name="Процент использования кредита (Utilization)",
        default=0.0,
        help_text="Остаток по кредиту / Лимит кредита"
    )
    num_30_59_days_past_due = models.IntegerField(
        verbose_name="Количество просрочек (30-59 дней)",
        default=0,
        help_text="Количество раз, когда клиент был просрочен на 30-59 дней"
    )
    debt_ratio = models.FloatField(
        verbose_name="Коэффициент долговой нагрузки (DebtRatio)",
        default=0.0,
        help_text="Ежемесячные платежи по долгам / Ежемесячный доход"
    )
    monthly_income = models.FloatField(
        verbose_name="Ежемесячный доход (MonthlyIncome)",
        null=True, # Может быть null, если доход неизвестен
        blank=True, # Может быть пустым в форме
        default=0.0,
        help_text="Ежемесячный доход клиента"
    )
    num_credit_lines_loans = models.IntegerField(
        verbose_name="Количество кредитных линий/займов (NumCreditLinesLoans)",
        default=0,
        help_text="Количество активных кредитных линий и/или займов"
    )

    created_at = models.DateTimeField(default=timezone.now, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата последнего обновления")


    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"
        ordering = ['full_name']


    def __str__(self):
        return f"{self.full_name} (ИНН: {self.inn})"