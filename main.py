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
# BỘ NGÔN NGỮ CHUẨN 4 TIẾNG (ĐÃ GIẢM BỚT BƯỚC)
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
            "• Regular updates"
        ),
        'btn_annual': "Annually $45 (65% OFF)",
        'btn_monthly': "Monthly $11",
        'btn_overview': "View the channel overview",
        'select_pay': "Choose a payment method",
        'btn_card': "💳 Apple Pay/Card",
        'btn_crypto': "🏴‍☠️ Crypto",
        'btn_back': "Back",
        'card_msg': "*Click Request Invoice*\n\nOur manager will send you payment instructions for Card/Apple Pay.",
        'crypto_msg': "*Click Contact Manager*\n\nOur manager will provide you with the crypto deposit address (USDT / BTC) and instructions.",
        'btn_request_invoice': "Request Invoice ↗",
        'btn_contact_manager': "Contact Manager ↗",
        'invoice_card_text': "I want to pay by Card 💳",
        'invoice_crypto_text': "I want to pay by Crypto 🏴‍☠️",
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
            "• Actualizaciones regulares"
        ),
        'btn_annual': "Anual $45 (65% DESCUENTO)",
        'btn_monthly': "Mensual $11",
        'btn_overview': "Ver resumen del canal",
        'select_pay': "Elige un método de pago",
        'btn_card': "💳 Apple Pay/Tarjeta",
        'btn_crypto': "🏴‍☠️ Criptomonedas",
        'btn_back': "Atrás",
        'card_msg': "*Haz clic en Solicitar Factura*\n\nNuestro administrador te enviará las instrucciones de pago con tarjeta.",
        'crypto_msg': "*Haz clic en Contactar Administrador*\n\nNuestro administrador te proporcionará la dirección de depósito cripto (USDT / BTC) y las instrucciones.",
        'btn_request_invoice': "Solicitar Factura ↗",
        'btn_contact_manager': "Contactar Administrador ↗",
        'invoice_card_text': "Quiero pagar con tarjeta 💳",
        'invoice_crypto_text': "Quiero pagar con Criptomonedas 🏴‍☠️",
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
            "• Mises à jour régulières"
        ),
        'btn_annual': "Annuel 45$ (-65%)",
        'btn_monthly': "Mensuel 11$",
        'btn_overview': "Aperçu du canal",
        'select_pay': "Choisissez un mode de paiement",
        'btn_card': "💳 Apple Pay/Carte",
        'btn_crypto': "🏴‍☠️ Cryptomonnaie",
        'btn_back': "Retour",
        'card_msg': "*Cliquez sur Demander la facture*\n\nNotre responsable vous enverra les instructions pour le paiement par carte.",
        'crypto_msg': "*Cliquez sur Contacter le responsable*\n\nNotre responsable vous fournira l'adresse de dépôt crypto (USDT / BTC) et les instructions.",
        'btn_request_invoice': "Demander la facture ↗",
        'btn_contact_manager': "Contacter le responsable ↗",
        'invoice_card_text': "Je souhaite payer par carte 💳",
        'invoice_crypto_text': "Je souhaite payer par Cryptomonnaie 🏴‍☠️",
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
            "• Atualizações regulares"
        ),
        'btn_annual': "Anual $45 (65% OFF)",
        'btn_monthly': "Mensal $11",
        'btn_overview': "Ver visão geral do canal",
        'select_pay': "Escolha uma forma de pagamento",
        'btn_card': "💳 Apple Pay/Cartão",
        'btn_crypto': "🏴‍☠️ Cripto",
        'btn_back': "Voltar",
        'card_msg': "*Clique em Solicitar Fatura*\n\nNosso gerente enviará as instruções para pagamento via cartão.",
        'crypto_msg': "*Clique em Falar com Gerente*\n\nNosso gerente fornecerá o endereço para depósito em cripto (USDT / BTC) e as instruções.",
        'btn_request_invoice': "Solicitar Fatura ↗",
        'btn_contact_manager': "Falar com Gerente ↗",
        'invoice_card_text': "Quero pagar via cartão 💳",
        'invoice_crypto_text': "Quero pagar via Cripto 🏴‍☠️",
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
        keyboard = [
            [InlineKeyboardButton(t['btn_annual'], callback_data='pkg_45')],
            [InlineKeyboardButton(t['btn_monthly'], callback_data='pkg_11')],
            [InlineKeyboardButton(t['btn_overview'], url=f"https://t.me/{ADMIN_USERNAME}")]
        ]
        await query.edit_message_text(t['intro'].format(name=user_name), reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    elif data.startswith('pkg_'):
        lang = context.user_data.get('lang', 'en')
        t = TEXTS[lang]
        context.user_data['amount'] = "45" if "45" in data else "11"
        keyboard = [
            [InlineKeyboardButton(t['btn_card'], callback_data='pay_card')],
            [InlineKeyboardButton(t['btn_crypto'], callback_data='pay_crypto')],
            [InlineKeyboardButton(t['btn_back'], callback_data=f"lang_{lang}")]
        ]
        await query.edit_message_text(t['select_pay'], reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    elif data == 'pay_card':
        lang = context.user_data.get('lang', 'en')
        t = TEXTS[lang]
        amount = context.user_data.get('amount', '11')
        
        encoded_text = quote(f"{t['invoice_card_text']} (${amount})")
        chat_url = f"https://t.me/{ADMIN_USERNAME}?text={encoded_text}"
        
        keyboard = [
            [InlineKeyboardButton(t['btn_request_invoice'], url=chat_url)],
            [InlineKeyboardButton(t['btn_back'], callback_data='pkg_' + amount)]
        ]
        await query.edit_message_text(t['card_msg'], reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    elif data == 'pay_crypto':
        lang = context.user_data.get('lang', 'en')
        t = TEXTS[lang]
        amount = context.user_data.get('amount', '11')

        encoded_text = quote(f"{t['invoice_crypto_text']} (${amount})")
        chat_url = f"https://t.me/{ADMIN_USERNAME}?text={encoded_text}"

        keyboard = [
            [InlineKeyboardButton(t['btn_contact_manager'], url=chat_url)],
            [InlineKeyboardButton(t['btn_back'], callback_data='pkg_' + amount)]
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
