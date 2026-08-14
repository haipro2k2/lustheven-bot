import os
import asyncio
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

app = Flask(__name__)

# ==========================================
# THÔNG TIN ĐÃ CẤU HÌNH SẴN CHO BẠN
# ==========================================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8507992829:AAE1e_c6MFQlEnggmd6LUvI-Vo27oPeeRco")
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "LHeaven_Admin")
ADMIN_ID = os.environ.get("ADMIN_ID", "1765008581")

# Ví Crypto
WALLET_USDT_TRC20 = "TSAmM5hX9bsNrHiMGHvfhJMNmxBpu9FHW6"
WALLET_USDT_BSC = "0x3cd89f6fe2a4159cddf559a56b9d70ac2225d1ec"
WALLET_BTC = "1Jucsph6cpJ7asnCeuM9qydqmd34xaNgwZ"

# Khởi tạo ứng dụng Bot
ptb_app = ApplicationBuilder().token(BOT_TOKEN).build()

# ==========================================
# BỘ NGÔN NGỮ chuẩn 4 TIẾNG (EN, ES, FR, PT)
# ==========================================
TEXTS = {
    'en': {
        'intro': "Hello, {name} 👋\n\nIn the premium channel, you'll find sizzling-hot content from the world's most stunning models. Get ready for an exclusive experience like no other!\n\n*By subscribing, you'll enjoy:*\n• Regular updates\n• Ad-free watching\n• Download to watch offline\n• High video quality\n• 10+ terabytes of content\n• Cancel anytime\n\nReady to unlock the forbidden allure?\n*Choose your plan 👇*",
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
        'intro': "Hola, {name} 👋\n\nEn el canal premium encontrarás contenido exclusivo de las modelos más impresionantes del mundo. ¡Prepárate para una experiencia única!\n\n*Al suscribirte, disfrutarás de:*\n• Actualizaciones regulares\n• Sin anuncios\n• Descarga para ver sin conexión\n• Alta calidad de video\n• Más de 10 terabytes de contenido\n• Cancela en cualquier momento\n\n¿Listo para acceder?\n*Elige tu plan 👇*",
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
        'intro': "Bonjour, {name} 👋\n\nDans le canal premium, vous trouverez du contenu exclusif des plus beaux modèles du monde. Préparez-vous pour une expérience unique !\n\n*En vous abonnant, vous bénéficierez de :*\n• Mises à jour régulières\n• Sans publicité\n• Téléchargement pour regarder hors ligne\n• Haute qualité vidéo\n• Plus de 10 téraoctets de contenu\n• Annulation à tout moment\n\nPrêt à débloquer l'accès ?\n*Choisissez votre formule 👇*",
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
        'intro': "Olá, {name} 👋\n\nNo canal premium, você encontrará conteúdo exclusivo das modelos mais incríveis do mundo. Prepare-se para uma experiência única!\n\n*Ao assinar, você terá:*\n• Atualizações regulares\n• Sem anúncios\n• Download para assistir offline\n• Alta qualidade de vídeo\n• Mais de 10 terabytes de conteúdo\n• Cancele quando quiser\n\nPronto para acessar?\n*Escolha seu plano 👇*",
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

# --- LỆNH /START ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("English", callback_data='lang_en'),
            InlineKeyboardButton("Español", callback_data='lang_es')
        ],
        [
            InlineKeyboardButton("Français", callback_data='lang_fr'),
            InlineKeyboardButton("Português", callback_data='lang_pt')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Choose your language",
        reply_markup=reply_markup
    )

# --- XỬ LÝ NÚT BẤM ---
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_name = query.from_user.first_name

    if data.startswith('lang_'):
        lang = data.replace('lang_', '')
        context.user_data['lang'] = lang
        t = TEXTS[lang]

        keyboard = [
            [InlineKeyboardButton(t['btn_annual'], callback_data='pkg_45')],
            [InlineKeyboardButton(t['btn_monthly'], callback_data='pkg_11')],
            [InlineKeyboardButton(t['btn_overview'], url=f"https://t.me/{ADMIN_USERNAME}")]
        ]
        await query.edit_message_text(
            t['intro'].format(name=user_name),
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

    elif data.startswith('pkg_'):
        lang = context.user_data.get('lang', 'en')
        t = TEXTS[lang]
        amount = "45" if "45" in data else "11"
        context.user_data['amount'] = amount

        keyboard = [
            [InlineKeyboardButton(t['btn_card'], callback_data='pay_card')],
            [InlineKeyboardButton(t['btn_stars'], callback_data='pay_stars')],
            [InlineKeyboardButton(t['btn_crypto'], callback_data='pay_crypto')],
            [InlineKeyboardButton(t['btn_back'], callback_data=f"lang_{lang}")]
        ]
        await query.edit_message_text(
            t['select_pay'],
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

    elif data == 'pay_card':
        lang = context.user_data.get('lang', 'en')
        t = TEXTS[lang]
        
        chat_url = f"https://t.me/{ADMIN_USERNAME}?text={t['invoice_card_text'].replace(' ', '%20')}"
        keyboard = [
            [InlineKeyboardButton(t['btn_request_invoice'], url=chat_url)],
            [InlineKeyboardButton(t['btn_back'], callback_data='pkg_11')]
        ]
        await query.edit_message_text(
            t['card_msg'],
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

    elif data == 'pay_crypto':
        lang = context.user_data.get('lang', 'en')
        t = TEXTS[lang]

        keyboard = [
            [
                InlineKeyboardButton("USDT (TRC20)", callback_data='coin_trc20'),
                InlineKeyboardButton("USDT (BSC)", callback_data='coin_bsc')
            ],
            [
                InlineKeyboardButton("BTC", callback_data='coin_btc')
            ],
            [InlineKeyboardButton(t['btn_back'], callback_data='pkg_11')]
        ]
        await query.edit_message_text(
            t['select_crypto'],
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

    elif data.startswith('coin_'):
        lang = context.user_data.get('lang', 'en')
        t = TEXTS[lang]
        amount = context.user_data.get('amount', '11')
        coin = data.replace('coin_', '')

        if coin == 'trc20':
            network_name = "TRC20"
            wallet = WALLET_USDT_TRC20
            msg_template = t['crypto_msg']
        elif coin == 'bsc':
            network_name = "BEP20 / BSC"
            wallet = WALLET_USDT_BSC
            msg_template = t['crypto_msg']
        else:
            network_name = "Bitcoin"
            wallet = WALLET_BTC
            msg_template = t['btc_msg']

        chat_text = t['invoice_crypto_text'].format(network=network_name)
        chat_url = f"https://t.me/{ADMIN_USERNAME}?text={chat_text.replace(' ', '%20')}"

        keyboard = [
            [InlineKeyboardButton(t['btn_contact_manager'], url=chat_url)],
            [InlineKeyboardButton(t['btn_back'], callback_data='pay_crypto')]
        ]
        
        display_msg = msg_template.format(amount=amount, network=network_name, wallet=wallet)
        
        await query.edit_message_text(
            display_msg,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

# Đăng ký Handlers
ptb_app.add_handler(CommandHandler("start", start))
ptb_app.add_handler(CallbackQueryHandler(handle_buttons))

# ==========================================
# VERCEL WEBHOOK ROUTE
# ==========================================
@app.route("/", methods=["POST"])
def webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), ptb_app.bot)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(ptb_app.process_update(update))
        
        return "OK", 200
    return "Bad Request", 400

@app.route("/", methods=["GET"])
def index():
    return "Bot Telegram đang chạy mượt mà trên Vercel!", 200
