// static/employees_rag/scripts.js

document.addEventListener('DOMContentLoaded', function() {
    // Находим ключевые элементы на странице
    const chatBox = document.getElementById('chat-box');
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');

    // Функция для получения CSRF-токена из cookie (стандартная для Django)
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Функция для добавления нового сообщения в чат
    function appendMessage(message, className) {
        const messageElement = document.createElement('div');
        messageElement.className = 'message ' + className;
        messageElement.textContent = message;
        chatBox.appendChild(messageElement);
        // Автоматически прокручиваем чат вниз к последнему сообщению
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    // Обработчик отправки формы
    chatForm.addEventListener('submit', function(e) {
        e.preventDefault(); // Предотвращаем стандартную отправку формы

        const userMessage = userInput.value.trim(); // Получаем и очищаем текст пользователя
        if (userMessage === '') return; // Не отправляем пустые сообщения

        // 1. Отображаем сообщение пользователя в чате
        appendMessage(userMessage, 'user-message');
        userInput.value = ''; // Очищаем поле ввода

        // 2. Отправляем сообщение на сервер
        fetch('/employees_rag/send_message/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken') // Добавляем CSRF-токен для безопасности
            },
            body: JSON.stringify({ message: userMessage })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // 3. Отображаем ответ от бота
            appendMessage(data.response, 'bot-message');
        })
        .catch(error => {
            // 4. В случае ошибки, выводим сообщение об этом в чате
            console.error('There was a problem with the fetch operation:', error);
            appendMessage('Извините, произошла ошибка. Попробуйте еще раз.', 'bot-message');
        });
    });
});