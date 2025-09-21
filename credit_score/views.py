import os
from django.shortcuts import render
from django.conf import settings
from catboost import CatBoostClassifier
import pandas as pd

# Определение пути к модели
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
    initial_data = {} # <-- Очень важный словарь для сохранения данных формы

    # Отладочные сообщения
    print(f"\n[DEBUG VIEWS] Запрос: {request.method} на {request.path}")
    if request.method == 'POST':
        print("[DEBUG VIEWS] Обработка POST-запроса.")
        # Собираем данные из POST-запроса и сохраняем их для формы и для модели
        for feature in selected_features:
            value = request.POST.get(feature)
            initial_data[feature] = value # <-- Сохраняем введенное значение (строка) для HTML-поля 'value'
            print(f"[DEBUG VIEWS] Из POST: {feature} = '{value}'")

        if model:
            try:
                data_for_model = {}
                for feature in selected_features:
                    value = initial_data[feature] # Берем уже сохраненное значение
                    if value is None or value == '':
                        data_for_model[feature] = 0.0 # Для модели используем 0.0, если поле пустое
                    else:
                        try:
                            data_for_model[feature] = float(value) # Для модели преобразуем в float
                        except ValueError:
                            # Если преобразование в float не удалось, значит, пользователь ввел не число.
                            # Мы уже ловим ValueError ниже, но можно здесь добавить более детальную обработку.
                            raise ValueError(f"Некорректное числовое значение для поля '{feature_names_ru.get(feature, feature)}': '{value}'")


                print(f"[DEBUG VIEWS] Данные для модели: {data_for_model}")
                df = pd.DataFrame([data_for_model], columns=selected_features)
                prediction_proba = model.predict_proba(df)[:, 1]
                prediction = "Одобрен" if prediction_proba[0] >= 0.5 else "Отклонен"
                print(f"[DEBUG VIEWS] Прогноз: {prediction}, Вероятность: {prediction_proba[0]}")

            except ValueError as ve:
                prediction = f"Ошибка: Введены некорректные данные. {ve}"
                print(f"[DEBUG VIEWS ERROR] ValueError при обработке данных: {ve}")
            except Exception as e:
                prediction = f"Произошла неожиданная ошибка при предсказании: {e}"
                print(f"[DEBUG VIEWS ERROR] Неожиданная ошибка при предсказании: {e}")
        else:
            prediction = "Модель не загружена. Пожалуйста, проверьте логи сервера."
            print("[DEBUG VIEWS ERROR] Модель не загружена.")
    else: # GET-запрос
        print("[DEBUG VIEWS] Обработка GET-запроса (первое открытие или обновление).")
        # При первом открытии initial_data будет пустым,
        # что заполнит поля формы нулями благодаря |default:'0' в HTML.
        prediction = "Ожидаем ввода данных"


    return render(request, 'credit_score/predict.html', {
        'prediction': prediction,
        'features': selected_features,
        'feature_names_ru': feature_names_ru,
        'initial_data': initial_data, # <-- Передаем initial_data в шаблон
    })
