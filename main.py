import os
import asyncio
from urllib.parse import quote
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

app = Flask(__name__)

# ==========================================
# CẤU HÌNH THÔNG TIN BOT
# ==========================================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8507992829:AAE1e_c6MFQlEnggmd6LUvI-Vo27oPeeRco")
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "LHeaven_Admin").strip().lstrip('@')
ADMIN_ID = os.environ.get("ADMIN_ID", "1765008581")

# ==========================================
# BỘ NGÔN NGỮ CHUẨN 4 TIẾNG (1 GÓI $20 LIFETIME)
# ==========================================
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
        'select_pay': "Choose a payment method for **$20 Lifetime Access**:",
        'btn_card': "💳 Apple Pay/Card",
        'btn_crypto': "🏴‍☠️ Crypto",
        'btn_back': "Back to languages",
        'card_msg': "*Click Request Invoice*\n\nOur manager will send you payment instructions for Card/Apple Pay ($20).",
        'crypto_msg': "*Click Contact Manager*\n\nOur manager will provide you with the crypto deposit address (USDT / BTC) for $20 Lifetime access.",
        'btn_request_invoice': "Request Invoice ↗",
        'btn_contact_manager': "Contact Manager ↗",
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
        'select_pay': "Elige un método de pago para **Acceso de por vida ($20)**:",
        'btn_card': "💳 Apple Pay/Tarjeta",
        'btn_crypto': "🏴‍☠️ Criptomonedas",
        'btn_back': "Volver a idiomas",
        'card_msg': "*Haz clic en Solicitar Factura*\n\nNuestro administrador te enviará las instrucciones de pago con tarjeta ($20).",
        'crypto_msg': "*Haz clic en Contactar Administrador*\n\nNuestro administrador te proporcionará la dirección de depósito cripto (USDT / BTC) para el acceso de $20.",
        'btn_request_invoice': "Solicitar Factura ↗",
        'btn_contact_manager': "Contactar Administrador ↗",
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
        'select_pay': "Choisissez un mode de paiement pour **Accès à vie (20$)** :",
        'btn_card': "💳 Apple Pay/Carte",
        'btn_crypto': "🏴‍☠️ Cryptomonnaie",
        'btn_back': "Retour aux langues",
        'card_msg': "*Cliquez sur Demander la facture*\n\nNotre responsable vous enverra les instructions pour le paiement par carte (20$).",
        'crypto_msg': "*Cliquez sur Contacter le responsable*\n\nNotre responsable vous fournira l'adresse de dépôt crypto (USDT / BTC) pour l'accès à vie à 20$.",
        'btn_request_invoice': "Demander la facture ↗",
        'btn_contact_manager': "Contacter le responsable ↗",
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
        'select_pay': "Escolha uma forma de pagamento para **Acesso Vitalício ($20)**:",
        'btn_card': "💳 Apple Pay/Cartão",
        'btn_crypto': "🏴‍☠️ Cripto",
        'btn_back': "Voltar para idiomas",
        'card_msg': "*Clique em Solicitar Fatura*\n\nNosso gerente enviará as instruções para pagamento via cartão ($20).",
        'crypto_msg': "*Clique em Falar com Gerente*\n\nNosso gerente fornecerá o endereço para depósito em cripto (USDT / BTC) para o acesso vitalício de $20.",
        'btn_request_invoice': "Solicitar Fatura ↗",
        'btn_contact_manager': "Falar com Gerente ↗",
        'invoice_card_text': "Quero pagar $20 para acesso vitalício via cartão 💳",
        'invoice_crypto_text': "Quero pagar $20 para acesso vitalício via Cripto 🏴‍☠️",
    }
}

# --- CÁC HÀM XỬ LÝ LOGIC BOT ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("English", callback_data='lang_en'), InlineKeyboardButton("Español", callback_data='lang_es')],
        [InlineKeyboardButton("Français", callback_data='lang_fr'), InlineKeyboardButton("Português", callback_data='lang_pt')]
    ]
    await update.message.reply_text("Choose your language", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    user_name = query.from_user.first_name if query.from_user and query.from_user.first_name else "there"

    if data.startswith('lang_'):
        lang = data.replace('lang_', '')
        context.user_data['lang'] = lang
        t = TEXTS[lang]
        
        # Nhảy thẳng đến bước chọn thanh toán Card / Crypto
        keyboard = [
            [InlineKeyboardButton(t['btn_card'], callback_data='pay_card')],
            [InlineKeyboardButton(t['btn_crypto'], callback_data='pay_crypto')],
            [InlineKeyboardButton(t['btn_back'], callback_data='start_back')]
        ]
        await query.edit_message_text(t['intro'].format(name=user_name), reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    elif data == 'start_back':
        keyboard = [
            [InlineKeyboardButton("English", callback_data='lang_en'), InlineKeyboardButton("Español", callback_data='lang_es')],
            [InlineKeyboardButton("Français", callback_data='lang_fr'), InlineKeyboardButton("Português", callback_data='lang_pt')]
        ]
        await query.edit_message_text("Choose your language", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == 'pay_card':
        lang = context.user_data.get('lang', 'en')
        t = TEXTS[lang]
        
        encoded_text = quote(t['invoice_card_text'])
        chat_url = f"https://t.me/{ADMIN_USERNAME}?text={encoded_text}"
        
        keyboard = [
            [InlineKeyboardButton(t['btn_request_invoice'], url=chat_url)],
            [InlineKeyboardButton(t['btn_back'], callback_data=f"lang_{lang}")]
        ]
        await query.edit_message_text(t['card_msg'], reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    elif data == 'pay_crypto':
        lang = context.user_data.get('lang', 'en')
        t = TEXTS[lang]

        encoded_text = quote(t['invoice_crypto_text'])
        chat_url = f"https://t.me/{ADMIN_USERNAME}?text={encoded_text}"

        keyboard = [
            [InlineKeyboardButton(t['btn_contact_manager'], url=chat_url)],
            [InlineKeyboardButton(t['btn_back'], callback_data=f"lang_{lang}")]
        ]
        await query.edit_message_text(t['crypto_msg'], reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

# ==========================================
# KHỞI TẠO BOT DẠNG HÀM VERCEL WEBHOOK
# ==========================================
async def process_update_async(update_data):
    ptb_app = ApplicationBuilder().token(BOT_TOKEN).build()
    ptb_app.add_handler(CommandHandler("start", start))
    ptb_app.add_handler(CallbackQueryHandler(handle_buttons))
    
    async with ptb_app:
        await ptb_app.initialize()
        update = Update.de_json(update_data, ptb_app.bot)
        await ptb_app.process_update(update)

@app.route("/", methods=["POST"])
def webhook():
    if request.method == "POST":
        try:
            update_data = request.get_json(force=True)
            asyncio.run(process_update_async(update_data))
            return "OK", 200
        except Exception as e:
            print(f"Error handling update: {e}")
            return "Error", 500
    return "Bad Request", 400

@app.route("/", methods=["GET"])
def index():
    return "Bot Telegram đang chạy mượt mà trên Vercel!", 200
