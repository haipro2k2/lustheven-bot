import os
from flask import Flask, request
import requests

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8507992829:AAE1e_c6MFQlEnggmd6LUvI-Vo27oPeeRco")
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "LHeaven_Admin").strip().lstrip('@')
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

TEXTS = {
    'en': {
        'intro': "Hello, {name} 👋\n\nOur Premium channel features leaked videos of the most beautiful girls from OnlyFans / Artistic Nudity Photography...\n\n🔥 *Special Offer: $20 for Lifetime*",
        'btn_card': "💳 Apple Pay/Card",
        'btn_crypto': "🏴‍☠️ Crypto",
        'btn_back': "Back to languages",
        'card_msg': "*Click Request Invoice*\n\nOur manager will send you payment instructions for Card/Apple Pay ($20).",
        'crypto_msg': "*Click Contact Manager*\n\nOur manager will provide you with the crypto deposit address (USDT / BTC) for $20 Lifetime access.",
        'btn_request_invoice': "Request Invoice ↗",
        'btn_contact_manager': "Contact Manager ↗",
        'btn_back_pay': "Back",
        'invoice_card_text': "I want to pay $20 for Lifetime access by Card 💳",
        'invoice_crypto_text': "I want to pay $20 for Lifetime access by Crypto 🏴‍☠️",
    }
    # Thêm es, fr, pt tương tự nếu cần
}

def send_message(chat_id, text, reply_markup=None):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    requests.post(f"{TELEGRAM_API}/sendMessage", json=payload)

def edit_message(chat_id, message_id, text, reply_markup=None):
    payload = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": "Markdown"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    requests.post(f"{TELEGRAM_API}/editMessageText", json=payload)

def answer_callback(callback_query_id):
    requests.post(f"{TELEGRAM_API}/answerCallbackQuery", json={"callback_query_id": callback_query_id})

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    
    # Xử lý lệnh /start
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        if data["message"]["text"] == "/start":
            keyboard = {
                "inline_keyboard": [
                    [{"text": "English", "callback_data": "lang_en"}, {"text": "Español", "callback_data": "lang_es"}],
                    [{"text": "Français", "callback_data": "lang_fr"}, {"text": "Português", "callback_data": "lang_pt"}]
                ]
            }
            send_message(chat_id, "Choose your language", keyboard)

    # Xử lý khi bấm nút (Callback Query)
    elif "callback_query" in data:
        cb = data["callback_query"]
        cb_id = cb["id"]
        chat_id = cb["message"]["chat"]["id"]
        msg_id = cb["message"]["message_id"]
        cb_data = cb["data"]
        first_name = cb["from"].get("first_name", "there")

        answer_callback(cb_id) # Tắt icon quay quay ngay lập tức

        if cb_data.startswith("lang_"):
            lang = cb_data.replace("lang_", "")
            t = TEXTS.get(lang, TEXTS['en'])
            keyboard = {
                "inline_keyboard": [
                    [{"text": t['btn_card'], "callback_data": f"pay_card_{lang}"}],
                    [{"text": t['btn_crypto'], "callback_data": f"pay_crypto_{lang}"}],
                    [{"text": t['btn_back'], "callback_data": "start_back"}]
                ]
            }
            edit_message(chat_id, msg_id, t['intro'].format(name=first_name), keyboard)

        elif cb_data == "start_back":
            keyboard = {
                "inline_keyboard": [
                    [{"text": "English", "callback_data": "lang_en"}, {"text": "Español", "callback_data": "lang_es"}],
                    [{"text": "Français", "callback_data": "lang_fr"}, {"text": "Português", "callback_data": "lang_pt"}]
                ]
            }
            edit_message(chat_id, msg_id, "Choose your language", keyboard)

        elif cb_data.startswith("pay_card_"):
            lang = cb_data.replace("pay_card_", "")
            t = TEXTS.get(lang, TEXTS['en'])
            url = f"https://t.me/{ADMIN_USERNAME}?text={requests.utils.quote(t['invoice_card_text'])}"
            keyboard = {
                "inline_keyboard": [
                    [{"text": t['btn_request_invoice'], "url": url}],
                    [{"text": t['btn_back_pay'], "callback_data": f"lang_{lang}"}]
                ]
            }
            edit_message(chat_id, msg_id, t['card_msg'], keyboard)

        elif cb_data.startswith("pay_crypto_"):
            lang = cb_data.replace("pay_crypto_", "")
            t = TEXTS.get(lang, TEXTS['en'])
            url = f"https://t.me/{ADMIN_USERNAME}?text={requests.utils.quote(t['invoice_crypto_text'])}"
            keyboard = {
                "inline_keyboard": [
                    [{"text": t['btn_contact_manager'], "url": url}],
                    [{"text": t['btn_back_pay'], "callback_data": f"lang_{lang}"}]
                ]
            }
            edit_message(chat_id, msg_id, t['crypto_msg'], keyboard)

    return "OK", 200

@app.route("/", methods=["GET"])
def index():
    return "Bot Active", 200
