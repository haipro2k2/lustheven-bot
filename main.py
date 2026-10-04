import os
import urllib.parse
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Lấy token từ Environment Variables hoặc dùng Token của bạn
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8507992829:AAE87BpBU8CkC6P1bxOg-d65MMVg5A0h1oM")
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "LHeaven_Admin").strip().lstrip('@')
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

TEXTS = {
    'en': {
        'intro': (
            "Hello, {name} 👋\n\n"
            "Our Premium channel features leaked videos of the most beautiful girls from OnlyFans / Artistic Nudity Photography "
            "(College students, stage actresses, freelance fashion models)\n\n"
            "Subscription package includes:\n"
            "• One-time purchase for lifetime access\n"
            "• Free downloads\n"
            "• Over 3000 leaked models\n"
            "• Over 100,000 videos uploaded to Telegram\n"
            "• Best quality images and videos\n"
            "• Regular updates\n\n"
            "🔥 Special Offer: $20 for Lifetime"
        ),
        'btn_demo': "🎬 View Channel Demo ↗",
        'btn_card': "💳 Apple Pay/Card",
        'btn_crypto': "🏴‍☠️ Crypto",
        'btn_back': "Back to languages",
        'card_msg': "Click Request Invoice\n\nOur manager will send you payment instructions for Card/Apple Pay ($20).",
        'crypto_msg': "Click Contact Manager\n\nOur manager will provide you with the crypto deposit address (USDT / BTC) for $20 Lifetime access.",
        'btn_request_invoice': "Request Invoice ↗",
        'btn_contact_manager': "Contact Manager ↗",
        'btn_back_pay': "Back",
        'invoice_card_text': "I want to pay $20 for Lifetime access by Card 💳",
        'invoice_crypto_text': "I want to pay $20 for Lifetime access by Crypto 🏴‍☠️",
        'demo_request_text': "Hello! Please send me the preview/demo video of the Premium Channel 🎬",
    },
    'es': {
        'intro': (
            "Hola, {name} 👋\n\n"
            "Nuestro canal Premium presenta videos filtrados de las chicas más bellas de OnlyFans / Fotografía Artística de Desnudez "
            "(estudiantes universitarias, actrices de teatro, modelos independientes).\n\n"
            "El paquete de suscripción incluye:\n"
            "• Compra única para acceso de por vida\n"
            "• Descargas gratuitas\n"
            "• Más de 3000 modelos con contenido filtrado\n"
            "• Más de 100 000 videos subidos a Telegram\n"
            "• Imágenes y videos de la mejor calidad\n"
            "• Actualizaciones regulares\n\n"
            "🔥 Oferta Especial: $20 de por vida"
        ),
        'btn_demo': "🎬 Ver Demo del Canal ↗",
        'btn_card': "💳 Apple Pay/Tarjeta",
        'btn_crypto': "🏴‍☠️ Criptomonedas",
        'btn_back': "Volver a idiomas",
        'card_msg': "Haz clic en Solicitar Factura\n\nNuestro administrador te enviará las instrucciones de pago con tarjeta ($20).",
        'crypto_msg': "Haz clic en Contactar Administrador\n\nNuestro administrador te proporcionará la dirección de depósito cripto (USDT / BTC) para el acceso de $20.",
        'btn_request_invoice': "Solicitar Factura ↗",
        'btn_contact_manager': "Contactar Administrador ↗",
        'btn_back_pay': "Atrás",
        'invoice_card_text': "Quiero pagar $20 de por vida con tarjeta 💳",
        'invoice_crypto_text': "Quiero pagar $20 de por vida con Criptomonedas 🏴‍☠️",
        'demo_request_text': "¡Hola! Por favor envíame el video de demostración del canal Premium 🎬",
    },
    'fr': {
        'intro': (
            "Bonjour, {name} 👋\n\n"
            "Notre canal Premium propose des vidéos d'infiltration des plus belles filles d'OnlyFans / Photographie de Nu Artistique "
            "(étudiantes universitaires, actrices de théâtre, mannequins indépendants).\n\n"
            "Le forfait d'abonnement comprend :\n"
            "• Achat unique pour un accès à vie\n"
            "• Téléchargements gratuits\n"
            "• Plus de 3 000 modèles exclusifs\n"
            "• Plus de 100 000 vidéos téléchargées sur Telegram\n"
            "• Images et vidéos de meilleure qualité\n"
            "• Mises à jour régulières\n\n"
            "🔥 Offre Spéciale : 20$ Accès à vie"
        ),
        'btn_demo': "🎬 Voir la démo du canal ↗",
        'btn_card': "💳 Apple Pay/Carte",
        'btn_crypto': "🏴‍☠️ Cryptomonnaie",
        'btn_back': "Retour aux langues",
        'card_msg': "Cliquez sur Demander la facture\n\nNotre responsable vous enverra les instructions pour le paiement par carte (20$).",
        'crypto_msg': "Cliquez sur Contacter le responsable\n\nNotre responsable vous fournira l'adresse de dépôt crypto (USDT / BTC) pour l'accès à vie à 20$.",
        'btn_request_invoice': "Demander la facture ↗",
        'btn_contact_manager': "Contacter le responsable ↗",
        'btn_back_pay': "Retour",
        'invoice_card_text': "Je souhaite payer 20$ pour l'accès à vie par carte 💳",
        'invoice_crypto_text': "Je souhaite payer 20$ pour l'accès à vie par Cryptomonnaie 🏴‍☠️",
        'demo_request_text': "Bonjour ! Veuillez m'envoyer la vidéo de démonstration du canal Premium 🎬",
    },
    'pt': {
        'intro': (
            "Olá, {name} 👋\n\n"
            "Nosso canal Premium apresenta vídeos vazados das garotas mais lindas do OnlyFans / Fotografia Artística de Nu "
            "(estudantes universitárias, atrizes de teatro, modelos independentes).\n\n"
            "O pacote de assinatura inclui:\n"
            "• Compra única para acesso vitalício\n"
            "• Downloads gratuitos\n"
            "• Mais de 3.000 modelos vazadas\n"
            "• Mais de 100.000 vídeos enviados para o Telegram\n"
            "• Imagens e vídeos de melhor qualidade\n"
            "• Atualizações regulares\n\n"
            "🔥 Oferta Especial: $20 Acesso Vitalício"
        ),
        'btn_demo': "🎬 Ver Demo do Canal ↗",
        'btn_card': "💳 Apple Pay/Cartão",
        'btn_crypto': "🏴‍☠️ Cripto",
        'btn_back': "Voltar para idiomas",
        'card_msg': "Clique em Solicitar Fatura\n\nNosso gerente enviará as instruções para pagamento via cartão ($20).",
        'crypto_msg': "Clique em Falar com Gerente\n\nNosso gerente fornecerá o endereço para depósito em cripto (USDT / BTC) para o acesso vitalício de $20.",
        'btn_request_invoice': "Solicitar Fatura ↗",
        'btn_contact_manager': "Falar com Gerente ↗",
        'btn_back_pay': "Voltar",
        'invoice_card_text': "Quero pagar $20 para acesso vitalício via cartão 💳",
        'invoice_crypto_text': "Quero pagar $20 para acesso vitalício via Cripto 🏴‍☠️",
        'demo_request_text': "Olá! Por favor me envie o vídeo de demonstração do canal Premium 🎬",
    }
}

def telegram_post(method, payload):
    try:
        res = requests.post(f"{TELEGRAM_API}/{method}", json=payload, timeout=5)
        return res.json()
    except Exception:
        return None

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json(force=True) or {}

    # 1. Xử lý câu lệnh /start từ tin nhắn
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        if data["message"]["text"].startswith("/start"):
            telegram_post("sendMessage", {
                "chat_id": chat_id,
                "text": "Choose your language",
                "reply_markup": {
                    "inline_keyboard": [
                        [{"text": "English", "callback_data": "lang_en"}, {"text": "Español", "callback_data": "lang_es"}],
                        [{"text": "Français", "callback_data": "lang_fr"}, {"text": "Português", "callback_data": "lang_pt"}]
                    ]
                }
            })
            return jsonify({"ok": True})

    # 2. Xử lý sự kiện bấm nút Inline
    elif "callback_query" in data:
        cb = data["callback_query"]
        cb_id = cb["id"]
        chat_id = cb["message"]["chat"]["id"]
        msg_id = cb["message"]["message_id"]
        cb_data = cb.get("data", "")
        first_name = cb.get("from", {}).get("first_name", "there")

        telegram_post("answerCallbackQuery", {"callback_query_id": cb_id})

        # Chọn Ngôn Ngữ -> Hiện menu chứa nút Xem Demo
        if cb_data.startswith("lang_"):
            lang = cb_data.replace("lang_", "")
            t = TEXTS.get(lang, TEXTS['en'])
            encoded_demo_msg = urllib.parse.quote(t['demo_request_text'])
            demo_url = f"https://t.me/{ADMIN_USERNAME}?text={encoded_demo_msg}"

            telegram_post("editMessageText", {
                "chat_id": chat_id,
                "message_id": msg_id,
                "text": t['intro'].format(name=first_name),
                "reply_markup": {
                    "inline_keyboard": [
                        [{"text": t['btn_demo'], "url": demo_url}],
                        [{"text": t['btn_card'], "callback_data": f"pay_card_{lang}"}],
                        [{"text": t['btn_crypto'], "callback_data": f"pay_crypto_{lang}"}],
                        [{"text": t['btn_back'], "callback_data": "start_back"}]
                    ]
                }
            })

        # Quay lại phần chọn ngôn ngữ
        elif cb_data == "start_back":
            telegram_post("editMessageText", {
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

        # Thanh toán qua Card
        elif cb_data.startswith("pay_card_"):
            lang = cb_data.replace("pay_card_", "")
            t = TEXTS.get(lang, TEXTS['en'])
            encoded_msg = urllib.parse.quote(t['invoice_card_text'])
            url = f"https://t.me/{ADMIN_USERNAME}?text={encoded_msg}"
            telegram_post("editMessageText", {
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

        # Thanh toán qua Crypto
        elif cb_data.startswith("pay_crypto_"):
            lang = cb_data.replace("pay_crypto_", "")
            t = TEXTS.get(lang, TEXTS['en'])
            encoded_msg = urllib.parse.quote(t['invoice_crypto_text'])
            url = f"https://t.me/{ADMIN_USERNAME}?text={encoded_msg}"
            telegram_post("editMessageText", {
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

        return jsonify({"ok": True})

    return jsonify({"ok": True})

@app.route("/", methods=["GET"])
def index():
    return "Bot is running!", 200
