from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime

app = Flask(__name__)

BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

print(f"[{datetime.utcnow()}] Bot started | Token present: {bool(BOT_TOKEN)}")

# Поддержка webhook с токеном в URL и без него
@app.route('/webhook', methods=['POST'])
@app.route('/<token>/webhook', methods=['POST'])   # для https://.../BOT_TOKEN/webhook
def telegram_webhook(token=None):
    try:
        update = request.get_json(silent=True)
        
        if not update or 'message' not in update:
            return jsonify({"ok": True}), 200

        message = update['message']
        chat_id = message['chat']['id']
        text = message.get('text', '').strip()

        print(f"[{datetime.utcnow()}] Received: {text} from {chat_id}")

        if text == '/start':
            resp = f"""👋 <b>Бот работает!</b>

✅ Webhook активен (Bothost)
🕒 {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

Напиши /help"""
        elif text == '/help':
            resp = "Команды:\n/start\n/help\n/status"
        else:
            resp = "Неизвестная команда → /help"

        if BOT_TOKEN:
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={"chat_id": chat_id, "text": resp, "parse_mode": "HTML"},
                timeout=10
            )

        return jsonify({"ok": True}), 200

    except Exception as e:
        print(f"Webhook error: {e}")
        return jsonify({"ok": True}), 200   # обязательно 200!


@app.route('/log-pin', methods=['POST'])
def log_pin():
    try:
        data = request.get_json(silent=True) or {}
        print(f"PIN log: {data.get('entered_pin')} | success={data.get('success')}")

        if CHAT_ID and BOT_TOKEN:
            status = "✅ Успешно" if data.get('success') else "❌ Неверно"
            msg = f"🔒 {status}\nPIN: <code>{data.get('entered_pin','—')}</code>"
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}
            )
        return jsonify({"ok": True}), 200
    except:
        return jsonify({"ok": True}), 200


@app.route('/')
def home():
    return "<h1>✅ Bot is running on Bothost</h1><p>Try /start in Telegram</p>"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
