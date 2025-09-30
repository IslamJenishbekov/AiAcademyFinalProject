# credit_score/views.py
import os
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from catboost import CatBoostClassifier
import pandas as pd
from .models import Client
from django.http import JsonResponse

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
    'inn': 'ИНН клиента',
    'full_name': 'ФИО клиента',
}


def predict_credit_approval(request):
    prediction = None
    initial_data = {}
    client_info = None
    input_inn = request.POST.get('inn', '').strip()  # ИНН из поля ввода
    action = request.POST.get('action', '')  # Какая кнопка была нажата

    print(f"\n[DEBUG VIEWS] Запрос: {request.method}, Action: '{action}', Input INN: '{input_inn}'")

    if request.method == 'POST':
        # При любом POST-запросе, если ИНН был введен, пытаемся его сохранить в initial_data
        initial_data['inn'] = input_inn

        # --- Логика для кнопки "Найти клиента" (action == 'check_inn') ---
        if action == 'check_inn':
            if input_inn:
                try:
                    client = Client.objects.get(inn=input_inn)
                    client_info = client
                    print(f"[DEBUG VIEWS] Клиент найден: {client.full_name}")
                    # Заполняем initial_data данными клиента для отображения и для передачи в скрытых полях
                    initial_data = {
                        'Utilization': client.utilization if client.utilization is not None else 0.0,
                        'age': client.age if client.age is not None else 0,
                        'Num30_59DaysPastDue': client.num_30_59_days_past_due if client.num_30_59_days_past_due is not None else 0,
                        'DebtRatio': client.debt_ratio if client.debt_ratio is not None else 0.0,
                        'MonthlyIncome': client.monthly_income if client.monthly_income is not None else 0.0,
                        'NumCreditLinesLoans': client.num_credit_lines_loans if client.num_credit_lines_loans is not None else 0,
                        'inn': client.inn,
                        'full_name': client.full_name,
                    }
                    # Сбрасываем prediction, чтобы не отображалось старое сообщение
                    prediction = None
                except Client.DoesNotExist:
                    print(f"[DEBUG VIEWS WARNING] Клиент с ИНН '{input_inn}' не найден.")
                    # Если клиент не найден, client_info остается None.
                    # Ручные поля ввода будут показаны. prediction останется None.
                    # Сообщение "Клиент не найден" будет в шаблоне через initial_data.inn и not client_info.
                    for feature in selected_features:  # Инициализируем ручные поля, если ИНН не найден
                        initial_data.setdefault(feature, '0')
                except Exception as e:
                    prediction = f"Ошибка при поиске клиента: {e}"
                    print(f"[DEBUG VIEWS ERROR] Общая ошибка при поиске клиента: {e}")
                    for feature in selected_features:
                        initial_data.setdefault(feature, '0')
            else:
                # Если ИНН не введен при нажатии 'check_inn', просто отображаем ручные поля
                prediction = "Пожалуйста, введите ИНН или данные вручную."
                for feature in selected_features:
                    initial_data.setdefault(feature, '0')

        # --- Логика для кнопки "Получить прогноз (по клиенту)" (action == 'get_prediction_from_found_client') ---
        elif action == 'get_prediction_from_found_client':
            # В этом случае client_info должен быть уже найден и передан в скрытых полях
            found_inn_from_hidden = request.POST.get('inn_found', '')  # Получаем ИНН из скрытого поля
            if found_inn_from_hidden:
                try:
                    client = Client.objects.get(inn=found_inn_from_hidden)
                    client_info = client  # Восстанавливаем client_info

                    # Заполняем initial_data данными клиента (снова) для рендера
                    initial_data = {
                        'Utilization': client.utilization if client.utilization is not None else 0.0,
                        'age': client.age if client.age is not None else 0,
                        'Num30_59DaysPastDue': client.num_30_59_days_past_due if client.num_30_59_days_past_due is not None else 0,
                        'DebtRatio': client.debt_ratio if client.debt_ratio is not None else 0.0,
                        'MonthlyIncome': client.monthly_income if client.monthly_income is not None else 0.0,
                        'NumCreditLinesLoans': client.num_credit_lines_loans if client.num_credit_lines_loans is not None else 0,
                        'inn': client.inn,
                        'full_name': client.full_name,
                    }

                    data_for_model = {feature: initial_data.get(feature) for feature in selected_features}
                    print(f"[DEBUG VIEWS] Данные для модели (из найденного клиента): {data_for_model}")

                    if model:
                        try:
                            df = pd.DataFrame([data_for_model], columns=selected_features)
                            prediction_proba = model.predict_proba(df)[:, 1]
                            print(f"Предикт:{prediction_proba}")
                            prediction = "Одобрен" if prediction_proba[0] <= 0.5 else "Отклонен"
                            print(f"[DEBUG VIEWS] Прогноз: {prediction}, Вероятность: {prediction_proba[0]:.4f}")
                        except Exception as e:
                            prediction = f"Ошибка при предсказании: {e}"
                            print(f"[DEBUG VIEWS ERROR] Неожиданная ошибка при предсказании: {e}")
                    else:
                        prediction = "Модель не загружена."
                except Client.DoesNotExist:
                    prediction = "Ошибка: Клиент не найден, хотя должен был быть."
                    print("[DEBUG VIEWS ERROR] Клиент не найден по скрытому ИНН.")
                except Exception as e:
                    prediction = f"Ошибка при обработке найденного клиента для предсказания: {e}"
                    print(f"[DEBUG VIEWS ERROR] Ошибка при обработке найденного клиента: {e}")
            else:
                prediction = "Ошибка: ИНН найденного клиента не передан."
                print("[DEBUG VIEWS ERROR] Скрытый ИНН не найден при попытке предсказания.")

        # --- Логика для кнопки "Получить прогноз (ручной ввод)" (action == 'get_prediction_from_manual_input') ---
        elif action == 'get_prediction_from_manual_input':
            data_for_model = {}
            has_error = False

            # Заполняем initial_data из POST-запроса для ручного ввода
            for feature in selected_features:
                value = request.POST.get(feature, '0')
                initial_data[feature] = value  # Сохраняем в initial_data для отображения
                if value is None or value == '':
                    data_for_model[feature] = 0.0
                else:
                    try:
                        data_for_model[feature] = float(value)
                    except ValueError:
                        prediction = f"Ошибка: Некорректное числовое значение для поля '{feature_names_ru.get(feature, feature)}': '{value}'"
                        print(f"[DEBUG VIEWS ERROR] ValueError при ручном вводе для '{feature}': {value}")
                        has_error = True
                        break  # Прерываем, если есть ошибка

            if not has_error:
                print(f"[DEBUG VIEWS] Данные для модели (ручной ввод): {data_for_model}")
                if model:
                    try:
                        df = pd.DataFrame([data_for_model], columns=selected_features)
                        prediction_proba = model.predict_proba(df)[0, 0]
                        print("Prediction", prediction_proba)
                        prediction = "Одобрен" if prediction_proba >= 0.5 else "Отклонен"
                        print(f"[DEBUG VIEWS] Прогноз: {prediction}, Вероятность: {prediction_proba:.4f}")
                    except Exception as e:
                        prediction = f"Произошла неожиданная ошибка при предсказании: {e}"
                        print(f"[DEBUG VIEWS ERROR] Неожиданная ошибка при предсказании: {e}")
                else:
                    prediction = "Модель не загружена."
            # Если была ошибка при парсинге, prediction уже установлен
            client_info = None  # Убеждаемся, что client_info сброшен при ручном вводе

        # Если POST-запрос не соответствовал ни одному из actions (например, просто отправили форму Enter-ом)
        else:
            prediction = "Действие не распознано. Пожалуйста, используйте кнопки."
            # Инициализируем поля для ручного ввода
            for feature in selected_features:
                initial_data.setdefault(feature, '0')


    else:  # GET-запрос (первая загрузка страницы)
        print("[DEBUG VIEWS] Обработка GET-запроса.")
        prediction = "Ожидаем ввода данных"
        # Инициализируем поля для ручного ввода и ИНН
        for feature in selected_features:
            initial_data[feature] = '0'
        initial_data['inn'] = ''


    return render(request, 'credit_score/predict.html', {
        'prediction': prediction,
        'features': selected_features,
        'feature_names_ru': feature_names_ru,
        'initial_data': initial_data,
        'client_info': client_info,
    })


def index_view(request):
    return render(request, 'credit_score/index.html')


# AJAX функция не меняется, если она используется для других целей
def get_client_data_ajax(request):
    print("[DEBUG AJAX] Получен AJAX-запрос на get_client_data_ajax")
    inn = request.GET.get('inn')
    client_data = {}
    if inn:
        try:
            client = Client.objects.get(inn=inn)
            client_data = {
                'found': True,
                'full_name': client.full_name,
                'utilization': client.utilization if client.utilization is not None else 0.0,
                'age': client.age if client.age is not None else 0,
                'num_30_59_days_past_due': client.num_30_59_days_past_due if client.num_30_59_days_past_due is not None else 0,
                'debt_ratio': client.debt_ratio if client.debt_ratio is not None else 0.0,
                'monthly_income': client.monthly_income if client.monthly_income is not None else 0.0,
                'num_credit_lines_loans': client.num_credit_lines_loans if client.num_credit_lines_loans is not None else 0,
            }
            print(f"[DEBUG AJAX] Клиент '{inn}' найден. Данные отправлены.")
        except Client.DoesNotExist:
            client_data = {'found': False, 'message': 'Клиент с таким ИНН не найден.'}
            print(f"[DEBUG AJAX] Клиент '{inn}' НЕ найден.")
        except Exception as e:
            client_data = {'found': False, 'message': f'Ошибка при поиске клиента: {e}'}
            print(f"[DEBUG AJAX ERROR] Ошибка при поиске клиента '{inn}': {e}")
    else:
        client_data = {'found': False, 'message': 'ИНН не предоставлен.'}
        print("[DEBUG AJAX] ИНН не был предоставлен.")
    return JsonResponse(client_data)