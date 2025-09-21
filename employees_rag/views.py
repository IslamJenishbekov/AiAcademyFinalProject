from django.shortcuts import render
from django.http import JsonResponse
import json
from employees_rag.services import rag_logic

def chat_page(request):
    return render(request, 'employees_rag/chat_page.html')

def send_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_message = data.get('message')

        # Получаем ответ от вашей логики
        bot_response = rag_logic.get_bot_response(user_message)

        return JsonResponse({'response': bot_response})
    return JsonResponse({'error': 'Invalid request'}, status=400)