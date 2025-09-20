# PycharmProjects/AiAcademyFinalProject/credit_score/views.py

import os
from django.shortcuts import render
from django.conf import settings
from catboost import CatBoostClassifier
import pandas as pd

MODEL_PATH = os.path.join(settings.BASE_DIR, 'credit_score', 'ml_models', 'my_catboost_model.cbm')

model = None
try:
    print(f"Попытка загрузить модель по пути: {MODEL_PATH}")
    loaded_model = CatBoostClassifier()
    loaded_model.load_model(MODEL_PATH)
    model = loaded_model
    print("Модель CatBoost успешно загружена.")
except Exception as e:
    print(f"!!! ОШИБКА !!! При загрузке модели CatBoost: {e}")

selected_features = [
    'Utilization',
    'age',
    'Num30_59DaysPastDue',
    'DebtRatio',
    'MonthlyIncome',
    'NumCreditLinesLoans',
]

feature_names_ru = {
    'Utilization': 'Процент использования кредита',
    'age': 'Возраст',
    'Num30_59DaysPastDue': 'Количество просрочек (30-59 дней)',
    'DebtRatio': 'Коэффициент долговой нагрузки',
    'MonthlyIncome': 'Ежемесячный доход',
    'NumCreditLinesLoans': 'Количество кредитных линий/займов',
}


def predict_credit_approval(request):
    prediction = None
    print(f"DEBUG: Метод запроса: {request.method}")  # DEBUG

    if request.method == 'POST':
        print("DEBUG: Получен POST-запрос.")  # DEBUG
        if model:
            print("DEBUG: Модель успешно загружена, пытаемся предсказать.")  # DEBUG
            try:
                data = {}
                for feature in selected_features:
                    value = request.POST.get(feature)
                    print(f"DEBUG: Получено поле '{feature}': '{value}'")  # DEBUG
                    if value is None or value == '':
                        # Используем значение по умолчанию, если поле пустое или None
                        data[feature] = 0.0
                        print(f"DEBUG: Поле '{feature}' пустое или None, используем 0.0")  # DEBUG
                    else:
                        data[feature] = float(value)

                print(f"DEBUG: Обработанные данные для предсказания: {data}")  # DEBUG
                df = pd.DataFrame([data], columns=selected_features)
                print(f"DEBUG: DataFrame для предсказания:\n{df}")  # DEBUG

                prediction_proba = model.predict_proba(df)[:, 1]
                prediction = "Одобрен" if prediction_proba[0] >= 0.5 else "Отклонен"
                print(f"DEBUG: Вероятность одобрения: {prediction_proba[0]}, Прогноз: {prediction}")  # DEBUG
            except ValueError as ve:
                prediction = f"Ошибка: Введены некорректные данные. Пожалуйста, введите числа. (Детали: {ve})"
                print(f"ERROR: ValueError при обработке данных: {ve}")  # DEBUG
            except Exception as e:
                prediction = f"Произошла ошибка при предсказании: {e}"
                print(f"ERROR: Неожиданная ошибка при предсказании: {e}")  # DEBUG
        else:
            prediction = "Модель не загружена. Пожалуйста, проверьте логи сервера."
            print("ERROR: Модель не загружена в predict_credit_approval.")  # DEBUG
    else:
        # Для GET-запроса или первого открытия страницы
        prediction = "Ожидаем ввода данных"
        print("DEBUG: Получен GET-запрос, отображаем форму.")  # DEBUG

    return render(request, 'credit_score/predict.html', {
        'prediction': prediction,
        'features': selected_features,
        'feature_names_ru': feature_names_ru,
    })