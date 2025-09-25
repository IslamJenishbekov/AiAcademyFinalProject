import os
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from catboost import CatBoostClassifier
import pandas as pd
from .models import Client  # Импортируем вашу модель Client

# Определение пути к модели
MODEL_PATH = os.path.join(settings.BASE_DIR, 'credit_score', 'ml_models', 'my_catboost_model.cbm')

model = None
try:
    print(f"Попытка загрузить модель по пути: {MODEL_PATH}")
    loaded_model = CatBoostClassifier()
    # Убедитесь, что вы загружаете модель с теми же параметрами, с которыми она была сохранена
    # Если у вас есть какие-либо параметры, передайте их здесь, например:
    # loaded_model = CatBoostClassifier(random_seed=42)
    loaded_model.load_model(MODEL_PATH)
    model = loaded_model
    print("Модель CatBoost успешно загружена.")
except Exception as e:
    print(f"!!! ОШИБКА !!! При загрузке модели CatBoost: {e}")

# Список признаков, используемых моделью CatBoost
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
    initial_data = {}
    # Получаем всех клиентов для выпадающего списка
    clients = Client.objects.all().order_by('full_name')
    selected_client_id = None
    client_info = None # Для хранения объекта клиента, если он выбран

    print(f"\n[DEBUG VIEWS] Запрос: {request.method} на {request.path}")

    if request.method == 'POST':
        print("[DEBUG VIEWS] Обработка POST-запроса.")
        selected_client_id_str = request.POST.get('client_id')

        # Если выбран постоянный клиент (ID не 'None' и не пустая строка)
        if selected_client_id_str and selected_client_id_str != 'None':
            try:
                selected_client_id = int(selected_client_id_str)
                print(f"[DEBUG VIEWS] Выбран постоянный клиент с ID: {selected_client_id}")
                client = get_object_or_404(Client, pk=selected_client_id)
                client_info = client # Сохраняем объект клиента для отображения

                # Заполняем initial_data и data_for_model данными клиента
                initial_data = {
                    'Utilization': client.utilization if client.utilization is not None else 0.0,
                    'age': client.age if client.age is not None else 0,
                    'Num30_59DaysPastDue': client.num_30_59_days_past_due if client.num_30_59_days_past_due is not None else 0,
                    'DebtRatio': client.debt_ratio if client.debt_ratio is not None else 0.0,
                    'MonthlyIncome': client.monthly_income if client.monthly_income is not None else 0.0,
                    'NumCreditLinesLoans': client.num_credit_lines_loans if client.num_credit_lines_loans is not None else 0,
                }
                data_for_model = initial_data.copy() # Для модели используем те же данные
                print(f"[DEBUG VIEWS] Данные для модели (постоянный клиент): {data_for_model}")

            except (ValueError, Client.DoesNotExist) as e:
                prediction = f"Ошибка: Выбранный клиент не найден или некорректный ID. {e}"
                print(f"[DEBUG VIEWS ERROR] Ошибка при получении данных клиента: {e}")
            except Exception as e:
                prediction = f"Произошла ошибка при получении данных клиента: {e}"
                print(f"[DEBUG VIEWS ERROR] Общая ошибка при получении данных клиента: {e}")

        else: # Данные вводятся вручную
            print("[DEBUG VIEWS] Данные вводятся вручную.")
            data_for_model = {}
            for feature in selected_features:
                value = request.POST.get(feature)
                initial_data[feature] = value # Сохраняем для отображения в полях

            for feature in selected_features:
                value = initial_data.get(feature) # Используем .get() для безопасного доступа
                if value is None or value == '':
                    data_for_model[feature] = 0.0
                else:
                    try:
                        data_for_model[feature] = float(value)
                    except ValueError:
                        prediction = f"Ошибка: Некорректное числовое значение для поля '{feature_names_ru.get(feature, feature)}': '{value}'"
                        print(f"[DEBUG VIEWS ERROR] ValueError при ручном вводе для '{feature}': {value}")
                        # Прерываем обработку и возвращаем ошибку
                        return render(request, 'credit_score/predict.html', {
                            'prediction': prediction,
                            'features': selected_features,
                            'feature_names_ru': feature_names_ru,
                            'initial_data': initial_data,
                            'clients': clients,
                            'selected_client_id': selected_client_id,
                            'client_info': client_info,
                        })
            print(f"[DEBUG VIEWS] Данные для модели (ручной ввод): {data_for_model}")


        # Если данные для модели были успешно сформированы и модель загружена
        if model and 'data_for_model' in locals() and not prediction:
            try:
                df = pd.DataFrame([data_for_model], columns=selected_features)
                prediction_proba = model.predict_proba(df)[:, 1] # Вероятность класса 1 (одобрен)
                prediction = "Одобрен" if prediction_proba[0] >= 0.5 else "Отклонен"
                print(f"[DEBUG VIEWS] Прогноз: {prediction}, Вероятность: {prediction_proba[0]:.4f}")

            except Exception as e:
                prediction = f"Произошла неожиданная ошибка при предсказании: {e}"
                print(f"[DEBUG VIEWS ERROR] Неожиданная ошибка при предсказании: {e}")
        elif not model and not prediction:
            prediction = "Модель не загружена. Пожалуйста, проверьте логи сервера."
            print("[DEBUG VIEWS ERROR] Модель не загружена.")

    else: # GET-запрос
        print("[DEBUG VIEWS] Обработка GET-запроса.")
        prediction = "Ожидаем ввода данных"
        # Устанавливаем начальные значения для полей ввода при первом GET-запросе
        for feature in selected_features:
            initial_data[feature] = '0'

    return render(request, 'credit_score/predict.html', {
        'prediction': prediction,
        'features': selected_features,
        'feature_names_ru': feature_names_ru,
        'initial_data': initial_data,
        'clients': clients, # Передаем список клиентов
        'selected_client_id': selected_client_id, # Передаем ID выбранного клиента
        'client_info': client_info, # Передаем объект клиента, если он выбран
    })