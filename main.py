import os
import urllib.parse
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8507992829:AAE1e_c6MFQlEnggmd6LUvI-Vo27oPeeRco")
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "LHeaven_Admin").strip().lstrip('@')
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

TEXTS = {
    'en': {
        'intro': (
            "Hello, {name} 👋\n\nOur Premium channel features leaked videos of the most beautiful girls from OnlyFans / Artistic Nudity Photography "
            "(College students, stage actresses, freelance fashion models)\n\n"
            "Subscription package includes:\n\n"
            "One-time purchase for lifetime access\n\n"
            "Free downloads\n\n"
            "• Over 3000 leaked models\n\n"
            "• Over 100,000 videos uploaded to Telegram\n\n"
            "• Best quality images and videos\n\n"
            "• Regular updates\n\n"
            "🔥 **Special Offer: $20 for Lifetime**"
        ),
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
    },
    'es': {
        'intro': (
            "Hola, {name} 👋\n\nNuestro canal Premium presenta videos filtrados de las chicas más bellas de OnlyFans / Fotografía Artística de Desnudez "
            "(estudiantes universitarias, actrices de teatro, modelos independientes).\n\n"
            "El paquete de suscripción incluye:\n\n"
            "Compra única para acceso de por vida\n\n"
            "Descargas gratuitas\n\n"
            "• Más de 3000 modelos con contenido filtrado\n\n"
            "• Más de 100 000 videos subidos a Telegram\n\n"
            "• Imágenes y videos de la mejor calidad\n\n"
            "• Actualizaciones regulares\n\n"
            "🔥 **Oferta Especial: $20 de por vida**"
        ),
        'btn_card': "💳 Apple Pay/Tarjeta",
        'btn_crypto': "🏴‍☠️ Criptomonedas",
        'btn_back': "Volver a idiomas",
        'card_msg': "*Haz clic en Solicitar Factura*\n\nNuestro administrador te enviará las instrucciones de pago con tarjeta ($20).",
        'crypto_msg': "*Haz clic en Contactar Administrador*\n\nNuestro administrador te proporcionará la dirección de depósito cripto (USDT / BTC) para el acceso de $20.",
        'btn_request_invoice': "Solicitar Factura ↗",
        'btn_contact_manager': "Contactar Administrador ↗",
        'btn_back_pay': "Atrás",
        'invoice_card_text': "Quiero pagar $20 de por vida con tarjeta 💳",
        'invoice_crypto_text': "Quiero pagar $20 de por vida con Criptomonedas 🏴‍☠️",
    },
    'fr': {
        'intro': (
            "Bonjour, {name} 👋\n\nNotre canal Premium propose des vidéos d'infiltration des plus belles filles d'OnlyFans / Photographie de Nu Artistique "
            "(étudiantes universitaires, actrices de théâtre, mannequins indépendants).\n\n"
            "Le forfait d'abonnement comprend :\n\n"
            "Achat unique pour un accès à vie\n\n"
            "Téléchargements gratuits\n\n"
            "• Plus de 3 000 modèles exclusifs\n\n"
            "• Plus de 100 000 vidéos téléchargées sur Telegram\n\n"
            "• Images et vidéos de meilleure qualité\n\n"
            "• Mises à jour régulières\n\n"
            "🔥 **Offre Spéciale : 20$ Accès à vie**"
        ),
        'btn_card': "💳 Apple Pay/Carte",
        'btn_crypto': "🏴‍☠️ Cryptomonnaie",
        'btn_back': "Retour aux langues",
        'card_msg': "*Cliquez sur Demander la facture*\n\nNotre responsable vous enverra les instructions pour le paiement par carte (20$).",
        'crypto_msg': "*Cliquez sur Contacter le responsable*\n\nNotre responsable vous fournira l'adresse de dépôt crypto (USDT / BTC) pour l'accès à vie à 20$.",
        'btn_request_invoice': "Demander la facture ↗",
        'btn_contact_manager': "Contacter le responsable ↗",
        'btn_back_pay': "Retour",
        'invoice_card_text': "Je souhaite payer 20$ pour l'accès à vie par carte 💳",
        'invoice_crypto_text': "Je souhaite payer 20$ pour l'accès à vie par Cryptomonnaie 🏴‍☠️",
    },
    'pt': {
        'intro': (
            "Olá, {name} 👋\n\nNosso canal Premium apresenta vídeos vazados das garotas mais lindas do OnlyFans / Fotografia Artística de Nu "
            "(estudantes universitárias, atrizes de teatro, modelos independentes).\n\n"
            "O pacote de assinatura inclui:\n\n"
            "Compra única para acesso vitalício\n\n"
            "Downloads gratuitos\n\n"
            "• Mais de 3.000 modelos vazadas\n\n"
            "• Mais de 100.000 vídeos enviados para o Telegram\n\n"
            "• Imagens e vídeos de melhor qualidade\n\n"
            "• Atualizações regulares\n\n"
            "🔥 **Oferta Especial: $20 Acesso Vitalício**"
        ),
        'btn_card': "💳 Apple Pay/Cartão",
        'btn_crypto': "🏴‍☠️ Cripto",
        'btn_back': "Voltar para idiomas",
        'card_msg': "*Clique em Solicitar Fatura*\n\nNosso gerente enviará as instruções para pagamento via cartão ($20).",
        'crypto_msg': "*Clique em Falar com Gerente*\n\nNosso gerente fornecerá o endereço para depósito em cripto (USDT / BTC) para o acesso vitalício de $20.",
        'btn_request_invoice': "Solicitar Fatura ↗",
        'btn_contact_manager': "Falar com Gerente ↗",
        'btn_back_pay': "Voltar",
        'invoice_card_text': "Quero pagar $20 para acesso vitalício via cartão 💳",
        'invoice_crypto_text': "Quero pagar $20 para acesso vitalício via Cripto 🏴‍☠️",
    }
}

def stop_button_loading(cb_id):
    """Gửi lệnh tắt ngay lập tức vòng xoay loading của nút bấm trên Telegram"""
    try:
        requests.post(f"{TELEGRAM_API}/answerCallbackQuery", json={"callback_query_id": cb_id}, timeout=2)
    except Exception:
        pass

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json(force=True) or {}

    # 1. Người dùng bấm /start
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        if data["message"]["text"] == "/start":
            return jsonify({
                "method": "sendMessage",
                "chat_id": chat_id,
                "text": "Choose your language",
                "reply_markup": {
                    "inline_keyboard": [
                        [{"text": "English", "callback_data": "lang_en"}, {"text": "Español", "callback_data": "lang_es"}],
                        [{"text": "Français", "callback_data": "lang_fr"}, {"text": "Português", "callback_data": "lang_pt"}]
                    ]
                }
            })

    # 2. Người dùng bấm nút (Callback Query)
    elif "callback_query" in data:
        cb = data["callback_query"]
        cb_id = cb["id"]
        chat_id = cb["message"]["chat"]["id"]
        msg_id = cb["message"]["message_id"]
        cb_data = cb.get("data", "")
        first_name = cb.get("from", {}).get("first_name", "there")

        # Tắt vòng xoay ngay lập tức
        stop_button_loading(cb_id)

        # 2a. Chọn ngôn ngữ
        if cb_data.startswith("lang_"):
            lang = cb_data.replace("lang_", "")
            t = TEXTS.get(lang, TEXTS['en'])
            return jsonify({
                "method": "editMessageText",
                "chat_id": chat_id,
                "message_id": msg_id,
                "text": t['intro'].format(name=first_name),
                "reply_markup": {
                    "inline_keyboard": [
                        [{"text": t['btn_card'], "callback_data": f"pay_card_{lang}"}],
                        [{"text": t['btn_crypto'], "callback_data": f"pay_crypto_{lang}"}],
                        [{"text": t['btn_back'], "callback_data": "start_back"}]
                    ]
                }
            })

        # 2b. Quay lại chọn ngôn ngữ
        elif cb_data == "start_back":
            return jsonify({
                "method": "editMessageText",
                "chat_id": chat_id,
                "message_id": msg_id,
                "text": "Choose your language",
                "reply_markup": {
                    "inline_keyboard": [
                        [{"text": "English", "callback_data": "lang_en"}, {"text": "Español", "callback_data": "lang_es"}],
                        [{"text": "Français", "callback_data": "lang_fr"}, {"text": "Português", "callback_data": "lang_pt"}]
                    ]
                }
            })

        # 2c. Chọn CARD
        elif cb_data.startswith("pay_card_"):
            lang = cb_data.replace("pay_card_", "")
            t = TEXTS.get(lang, TEXTS['en'])
            encoded_msg = urllib.parse.quote(t['invoice_card_text'])
            url = f"https://t.me/{ADMIN_USERNAME}?text={encoded_msg}"
            return jsonify({
                "method": "editMessageText",
                "chat_id": chat_id,
                "message_id": msg_id,
                "text": t['card_msg'],
                "reply_markup": {
                    "inline_keyboard": [
                        [{"text": t['btn_request_invoice'], "url": url}],
                        [{"text": t['btn_back_pay'], "callback_data": f"lang_{lang}"}]
                    ]
                }
            })

        # 2d. Chọn CRYPTO
        elif cb_data.startswith("pay_crypto_"):
            lang = cb_data.replace("pay_crypto_", "")
            t = TEXTS.get(lang, TEXTS['en'])
            encoded_msg = urllib.parse.quote(t['invoice_crypto_text'])
            url = f"https://t.me/{ADMIN_USERNAME}?text={encoded_msg}"
            return jsonify({
                "method": "editMessageText",
                "chat_id": chat_id,
                "message_id": msg_id,
                "text": t['crypto_msg'],
                "reply_markup": {
                    "inline_keyboard": [
                        [{"text": t['btn_contact_manager'], "url": url}],
                        [{"text": t['btn_back_pay'], "callback_data": f"lang_{lang}"}]
                    ]
                }
            })

    return jsonify({"status": "ok"})

@app.route("/", methods=["GET"])
def index():
    return "Bot Active!", 200
