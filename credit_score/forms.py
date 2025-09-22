from django import forms

class CreditApplicationForm(forms.Form):
    utilization = forms.DecimalField(
        label='Utilization (Использование кредита)',
        max_digits=5, decimal_places=4,
        help_text='Общая сумма баланса по кредитным линиям / Кредитный лимит'
    )
    age = forms.IntegerField(
        label='Age (Возраст)',
        min_value=18, max_value=120
    )
    num_30_59_days_past_due = forms.IntegerField(
        label='Number of 30-59 days past due (Кол-во просрочек 30-59 дней)',
        min_value=0
    )
    debt_ratio = forms.DecimalField(
        label='Debt Ratio (Коэффициент задолженности)',
        max_digits=7, decimal_places=4,
        help_text='Ежемесячные платежи по долгу / Ежемесячный доход'
    )
    monthly_income = forms.DecimalField(
        label='Monthly Income (Ежемесячный доход)',
        min_value=0, max_digits=10, decimal_places=2,
        help_text='Фактический ежемесячный доход'
    )
    num_credit_lines_loans = forms.IntegerField(
        label='Number of Credit Lines and Loans (Кол-во кредитных линий и займов)',
        min_value=0
    )