from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime

app = Flask(__name__)

BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')
WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET', 'mysecret123')  # для небольшой защиты

if not BOT_TOKEN or not CHAT_ID:
    print("⚠️ Внимание: BOT_TOKEN или CHAT_ID не установлены в переменных окружения!")

# ==================== ЛОГИРОВАНИЕ PIN ====================
@app.route('/log-pin', methods=['POST'])
def log_pin():
    try:
        data = request.get_json() or {}

        timestamp = data.get('timestamp', datetime.utcnow().isoformat() + 'Z')
        entered_pin = data.get('entered_pin', '—')
        success = data.get('success', False)
        ip = data.get('ip', 'неизвестно')
        user_agent = data.get('user_agent', '—')[:200]
        platform = data.get('platform', '—')
        language = data.get('language', '—')
        attempts = data.get('attempts', 0)

        status = "✅ Успешный вход" if success else "❌ Неверный PIN"

        message = f"""🔒 <b>Попытка ввода PIN</b>

🕒 {timestamp}
{status}
🔑 Введённый PIN: <code>{entered_pin}</code>
🔢 Попытка № {attempts}

🌐 IP: <code>{ip}</code>
📱 User-Agent: <code>{user_agent}</code>
🖥 Платформа: {platform} | Язык: {language}"""

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }

        r = requests.post(url, json=payload, timeout=10)
        if r.status_code != 200:
            print("Telegram send error:", r.text)

        return jsonify({"status": "ok"})
    except Exception as e:
        print("Ошибка в /log-pin:", str(e))
        return jsonify({"status": "error"}), 500


# ==================== ОБРАБОТКА КОМАНД TELEGRAM (/start и др.) ====================
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        update = request.get_json()

        if not update or 'message' not in update:
            return jsonify({"status": "ignored"})

        message = update['message']
        chat_id = message['chat']['id']
        text = message.get('text', '')

        if text == '/start':
            response_text = f"""👋 <b>Пин-логгер бот запущен и работает!</b>

✅ Бот онлайн
🔐 Готов принимать логи с HTML-страницы
📍 Логи приходят в этот чат

ID чата: <code>{chat_id}</code>
Время запуска: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

Просто напишите /help для справки."""

        elif text == '/help':
            response_text = """📋 Доступные команды:

/start — проверить, работает ли бот
/help — показать это сообщение
/status — информация о боте

Бот автоматически отправляет сюда все попытки ввода PIN с вашей защищённой страницы."""

        elif text == '/status':
            response_text = f"""📊 Статус бота:

🟢 Работает
⏰ Текущее время: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
📍 Логи отправляются в чат: {CHAT_ID}
🔗 Webhook активен"""

        else:
            response_text = "Неизвестная команда. Напишите /help"

        # Отправляем ответ
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": response_text,
            "parse_mode": "HTML"
        }
        requests.post(url, json=payload, timeout=8)

        return jsonify({"status": "ok"})
    except Exception as e:
        print("Ошибка в webhook:", str(e))
        return jsonify({"status": "error"}), 500


# Простая страница для проверки, что сервер живой
@app.route('/')
def home():
    return f"""
    <h1>Pin Logger Bot is running</h1>
    <p>Время: {datetime.utcnow()}</p>
    <p>Бот готов принимать логи по /log-pin</p>
    """

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
