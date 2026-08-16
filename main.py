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

# Địa chỉ ví Crypto
WALLET_USDT_TRC20 = "TSAmM5hX9bsNrHiMGHvfhJMNmxBpu9FHW6"
WALLET_USDT_BSC = "0x3cd89f6fe2a4159cddf559a56b9d70ac2225d1ec"
WALLET_BTC = "1Jucsph6cpJ7asnCeuM9qydqmd34xaNgwZ"

# ==========================================
# BỘ NGÔN NGỮ CHUẨN 4 TIẾNG (ĐÃ CẬP NHẬT THEO ẢNH)
# ==========================================
TEXTS = {
    'en': {
        'intro': (
            "Hello, {name} 👋\n\n Our Premium channel features leaked videos of the most beautiful girls from OnlyFans / Artistic Nudity Photography "
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
        'btn_stars': "⭐ Telegram Stars",
        'btn_crypto': "🏴‍☠️ Crypto",
        'btn_back': "Back",
        'select_crypto': "Choose your crypto / network",
        'card_msg': "*Click Request Invoice*\n\nOur manager will then send you instructions for payment by card",
        'btn_request_invoice': "Request Invoice ↗",
        'crypto_msg': "Send *{amount} USDT - Network {network}*, after payment contact our manager and she'll send you an invite to the premium channel\n\n`{wallet}`",
        'btc_msg': "Send *{amount}$ in BTC*, after payment contact our manager and she'll send you an invite to the premium channel\n\n`{wallet}`",
        'btn_contact_manager': "Contact manager ↗",
        'invoice_card_text': "I want to pay by card 💳",
        'invoice_crypto_text': "I sent payment ({network}), please check!",
    },
    'es': {
        'intro': (
            "Nuestro canal Premium presenta videos filtrados de las chicas más bellas de OnlyFans / Fotografía Artística de Desnudez "
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
        'btn_stars': "⭐ Telegram Stars",
        'btn_crypto': "🏴‍☠️ Criptomonedas",
        'btn_back': "Atrás",
        'select_crypto': "Elige tu criptomoneda / red",
        'card_msg': "*Haz clic en Solicitar Factura*\n\nNuestro administrador te enviará las instrucciones para pagar con tarjeta",
        'btn_request_invoice': "Solicitar Factura ↗",
        'crypto_msg': "Envía *{amount} USDT - Red {network}*, después del pago contacta a nuestro administrador para recibir tu invitación al canal premium\n\n`{wallet}`",
        'btc_msg': "Envía *{amount}$ en BTC*, después del pago contacta a nuestro administrador para recibir tu invitación al canal premium\n\n`{wallet}`",
        'btn_contact_manager': "Contactar Administrador ↗",
        'invoice_card_text': "Quiero pagar con tarjeta 💳",
        'invoice_crypto_text': "¡He enviado el pago ({network}), por favor verificar!",
    },
    'fr': {
        'intro': (
            "Notre canal Premium propose des vidéos d'infiltration des plus belles filles d'OnlyFans / Photographie de Nu Artistique "
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
        'btn_stars': "⭐ Telegram Stars",
        'btn_crypto': "🏴‍☠️ Cryptomonnaie",
        'btn_back': "Retour",
        'select_crypto': "Choisissez votre cryptomonnaie / réseau",
        'card_msg': "*Cliquez sur Demander la facture*\n\nNotre responsable vous enverra les instructions pour le paiement par carte",
        'btn_request_invoice': "Demander la facture ↗",
        'crypto_msg': "Envoyez *{amount} USDT - Réseau {network}*, après le paiement contactez notre responsable pour recevoir votre invitation\n\n`{wallet}`",
        'btc_msg': "Envoyez *{amount}$ en BTC*, après le paiement contactez notre responsable pour recevoir votre invitation\n\n`{wallet}`",
        'btn_contact_manager': "Contacter le responsable ↗",
        'invoice_card_text': "Je souhaite payer par carte 💳",
        'invoice_crypto_text': "J'ai envoyé le paiement ({network}), veuillez vérifier !",
    },
    'pt': {
        'intro': (
            "Nosso canal Premium apresenta vídeos vazados das garotas mais lindas do OnlyFans / Fotografia Artística de Nu "
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
        'btn_stars': "⭐ Telegram Stars",
        'btn_crypto': "🏴‍☠️ Cripto",
        'btn_back': "Voltar",
        'select_crypto': "Escolha sua criptomoeda / rede",
        'card_msg': "*Clique em Solicitar Fatura*\n\nNosso gerente enviará as instruções para pagamento via cartão",
        'btn_request_invoice': "Solicitar Fatura ↗",
        'crypto_msg': "Envie *{amount} USDT - Rede {network}*, após o pagamento entre em contato com nosso gerente para receber o convite\n\n`{wallet}`",
        'btc_msg': "Envie *{amount}$ em BTC*, após o pagamento entre em contato com nosso gerente para receber o convite\n\n`{wallet}`",
        'btn_contact_manager': "Falar com Gerente ↗",
        'invoice_card_text': "Quero pagar via cartão 💳",
        'invoice_crypto_text': "Enviei o pagamento ({network}), por favor verificar!",
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

    if data.startswith('lang_'):
        lang = data.replace('lang_', '')
        context.user_data['lang'] = lang
        t = TEXTS[lang]
        keyboard = [
            [InlineKeyboardButton(t['btn_annual'], callback_data='pkg_45')],
            [InlineKeyboardButton(t['btn_monthly'], callback_data='pkg_11')],
            [InlineKeyboardButton(t['btn_overview'], url=f"https://t.me/{ADMIN_USERNAME}")]
        ]
        await query.edit_message_text(t['intro'], reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    elif data.startswith('pkg_'):
        lang = context.user_data.get('lang', 'en')
        t = TEXTS[lang]
        context.user_data['amount'] = "45" if "45" in data else "11"
        keyboard = [
            [InlineKeyboardButton(t['btn_card'], callback_data='pay_card')],
            [InlineKeyboardButton(t['btn_stars'], callback_data='pay_stars')],
            [InlineKeyboardButton(t['btn_crypto'], callback_data='pay_crypto')],
            [InlineKeyboardButton(t['btn_back'], callback_data=f"lang_{lang}")]
        ]
        await query.edit_message_text(t['select_pay'], reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    elif data == 'pay_card':
        lang = context.user_data.get('lang', 'en')
        t = TEXTS[lang]
        
        encoded_text = quote(t['invoice_card_text'])
        chat_url = f"https://t.me/{ADMIN_USERNAME}?text={encoded_text}"
        
        keyboard = [
            [InlineKeyboardButton(t['btn_request_invoice'], url=chat_url)],
            [InlineKeyboardButton(t['btn_back'], callback_data='pkg_11')]
        ]
        await query.edit_message_text(t['card_msg'], reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    elif data == 'pay_crypto':
        lang = context.user_data.get('lang', 'en')
        t = TEXTS[lang]
        keyboard = [
            [InlineKeyboardButton("USDT (TRC20)", callback_data='coin_trc20'), InlineKeyboardButton("USDT (BSC)", callback_data='coin_bsc')],
            [InlineKeyboardButton("BTC", callback_data='coin_btc')],
            [InlineKeyboardButton(t['btn_back'], callback_data='pkg_11')]
        ]
        await query.edit_message_text(t['select_crypto'], reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    elif data.startswith('coin_'):
        lang = context.user_data.get('lang', 'en')
        t = TEXTS[lang]
        amount = context.user_data.get('amount', '11')
        coin = data.replace('coin_', '')

        if coin == 'trc20':
            network_name, wallet, msg_template = "TRC20", WALLET_USDT_TRC20, t['crypto_msg']
        elif coin == 'bsc':
            network_name, wallet, msg_template = "BEP20 / BSC", WALLET_USDT_BSC, t['crypto_msg']
        else:
            network_name, wallet, msg_template = "Bitcoin", WALLET_BTC, t['btc_msg']

        chat_text = t['invoice_crypto_text'].format(network=network_name)
        encoded_text = quote(chat_text)
        chat_url = f"https://t.me/{ADMIN_USERNAME}?text={encoded_text}"

        keyboard = [
            [InlineKeyboardButton(t['btn_contact_manager'], url=chat_url)],
            [InlineKeyboardButton(t['btn_back'], callback_data='pay_crypto')]
        ]
        await query.edit_message_text(msg_template.format(amount=amount, network=network_name, wallet=wallet), reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

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
