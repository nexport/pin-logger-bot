from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime

app = Flask(__name__)

BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        update = request.get_json(silent=True)
        if not update or 'message' not in update:
            return jsonify({"ok": True}), 200   # важно возвращать 200 OK

        message = update['message']
        chat_id = message['chat']['id']
        text = message.get('text', '').strip()

        if text == '/start':
            response = f"""👋 Бот работает!

✅ Webhook активен
🕒 {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
📍 Логи PIN приходят в этот чат

Напиши /help"""
        elif text == '/help':
            response = "Команды: /start, /help, /status"
        else:
            response = "Неизвестная команда. Напиши /help"

        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": response, "parse_mode": "HTML"},
            timeout=10
        )
        return jsonify({"ok": True}), 200
    except Exception as e:
        print("Webhook error:", e)
        return jsonify({"ok": True}), 200   # всегда 200, чтобы Telegram не ругался

@app.route('/setwebhook')
def set_webhook():
    if not BOT_TOKEN:
        return "<h1>BOT_TOKEN не найден в переменных окружения!</h1>"
    
    webhook_url = request.host_url.rstrip('/') + "/webhook"
    r = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={webhook_url}&drop_pending_updates=true")
    return f"""
    <h2>Webhook установлен</h2>
    <p>URL: <code>{webhook_url}</code></p>
    <pre>{r.text}</pre>
    <br><a href="/getwebhookinfo">Проверить статус webhook</a>
    """

@app.route('/getwebhookinfo')
def get_webhook_info():
    if not BOT_TOKEN:
        return "BOT_TOKEN не найден"
    r = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo")
    return f"<pre>{r.text}</pre>"

@app.route('/')
def home():
    return "<h1>Pin Logger Bot запущен</h1><p><a href='/setwebhook'>Установить webhook</a></p>"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
