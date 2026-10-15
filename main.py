import logging
import os
import urllib.parse
from flask import Flask, jsonify, request
import requests

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('telegram-bot')

BOT_TOKEN = os.environ.get('BOT_TOKEN', '').strip()
WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET', '').strip()
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', '').strip().lstrip('@')
DEMO_URL = os.environ.get('DEMO_URL', '').strip()
API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}'
SESSION = requests.Session()

LANGUAGES = {
    'en': {'title': 'Welcome, {name}! 👋\n\nDiscover our Premium channel and available membership options.\n\n⭐ Lifetime access: $20', 'demo': '🎬 View demo', 'card': '💳 Card / Apple Pay', 'crypto': '💠 Crypto', 'back': '⬅️ Back', 'card_info': 'Contact our manager to request card payment instructions.', 'crypto_info': 'Contact our manager to request cryptocurrency payment instructions.', 'contact': '✉️ Contact manager', 'invoice': 'Hello! I would like to request payment instructions for lifetime access by card.', 'crypto_request': 'Hello! I would like to request payment instructions for lifetime access by crypto.'},
    'es': {'title': '¡Hola, {name}! 👋\n\nDescubre nuestro canal Premium y las opciones de membresía.\n\n⭐ Acceso de por vida: 20 USD', 'demo': '🎬 Ver demostración', 'card': '💳 Tarjeta / Apple Pay', 'crypto': '💠 Cripto', 'back': '⬅️ Volver', 'card_info': 'Contacta al administrador para solicitar instrucciones de pago con tarjeta.', 'crypto_info': 'Contacta al administrador para solicitar instrucciones de pago con criptomonedas.', 'contact': '✉️ Contactar al administrador', 'invoice': 'Hola. Quiero solicitar instrucciones de pago con tarjeta.', 'crypto_request': 'Hola. Quiero solicitar instrucciones de pago con criptomonedas.'},
    'fr': {'title': 'Bonjour, {name} ! 👋\n\nDécouvrez notre chaîne Premium et les formules disponibles.\n\n⭐ Accès à vie : 20 USD', 'demo': '🎬 Voir la démo', 'card': '💳 Carte / Apple Pay', 'crypto': '💠 Crypto', 'back': '⬅️ Retour', 'card_info': 'Contactez notre responsable pour obtenir les instructions de paiement par carte.', 'crypto_info': 'Contactez notre responsable pour obtenir les instructions de paiement en cryptomonnaie.', 'contact': '✉️ Contacter le responsable', 'invoice': 'Bonjour ! Je souhaite recevoir les instructions de paiement par carte.', 'crypto_request': 'Bonjour ! Je souhaite recevoir les instructions de paiement en cryptomonnaie.'},
    'pt': {'title': 'Olá, {name}! 👋\n\nConheça nosso canal Premium e as opções de assinatura.\n\n⭐ Acesso vitalício: US$ 20', 'demo': '🎬 Ver demonstração', 'card': '💳 Cartão / Apple Pay', 'crypto': '💠 Cripto', 'back': '⬅️ Voltar', 'card_info': 'Entre em contato com o administrador para obter instruções de pagamento com cartão.', 'crypto_info': 'Entre em contato com o administrador para obter instruções de pagamento com criptomoedas.', 'contact': '✉️ Falar com o administrador', 'invoice': 'Olá! Gostaria de receber instruções de pagamento por cartão.', 'crypto_request': 'Olá! Gostaria de receber instruções de pagamento por cripto.'}
}


def tg(method, payload):
    try:
        response = SESSION.post(f'{API_URL}/{method}', json=payload, timeout=8)
        response.raise_for_status()
        result = response.json()
        if not result.get('ok'):
            logger.error('Telegram API %s: %s', method, result.get('description', 'unknown error'))
        return result
    except (requests.RequestException, ValueError) as exc:
        logger.error('Telegram request %s failed: %s', method, type(exc).__name__)
        return {'ok': False}


def language_menu():
    return {'inline_keyboard': [
        [{'text': '🇬🇧 English', 'callback_data': 'lang_en'}, {'text': '🇪🇸 Español', 'callback_data': 'lang_es'}],
        [{'text': '🇫🇷 Français', 'callback_data': 'lang_fr'}, {'text': '🇵🇹 Português', 'callback_data': 'lang_pt'}]
    ]}


def manager_url(text):
    if not ADMIN_USERNAME:
        return None
    return 'https://t.me/' + ADMIN_USERNAME + '?text=' + urllib.parse.quote(text, safe='')


def info_menu(lang):
    t = LANGUAGES[lang]
    rows = []
    if DEMO_URL.startswith('https://'):
        rows.append([{'text': t['demo'], 'url': DEMO_URL}])
    elif manager_url('Hello! Please send me a demo of your channel.'):
        rows.append([{'text': t['demo'], 'url': manager_url('Hello! Please send me a demo of your channel.')}])
    rows.extend([
        [{'text': t['card'], 'callback_data': 'card_' + lang}],
        [{'text': t['crypto'], 'callback_data': 'crypto_' + lang}],
        [{'text': t['back'], 'callback_data': 'back_languages'}]
    ])
    return {'inline_keyboard': rows}


def payment_menu(lang, method):
    t = LANGUAGES[lang]
    msg = t['invoice'] if method == 'card' else t['crypto_request']
    rows = []
    url = manager_url(msg)
    if url:
        rows.append([{'text': t['contact'], 'url': url}])
    rows.append([{'text': t['back'], 'callback_data': 'lang_' + lang}])
    return {'inline_keyboard': rows}


def handle_update(update):
    message = update.get('message', {})
    if message.get('text', '').split(' ', 1)[0].split('@')[0] == '/start':
        tg('sendMessage', {'chat_id': message['chat']['id'], 'text': '🌐 Choose your language / Selecciona tu idioma', 'reply_markup': language_menu()})
        return
    callback = update.get('callback_query')
    if not callback:
        return
    cb_id = callback.get('id')
    if cb_id:
        tg('answerCallbackQuery', {'callback_query_id': cb_id})
    msg = callback.get('message', {})
    if not msg.get('chat') or not msg.get('message_id'):
        return
    data = callback.get('data', '')
    chat_id, message_id = msg['chat']['id'], msg['message_id']
    if data == 'back_languages':
        text, menu = '🌐 Choose your language / Selecciona tu idioma', language_menu()
    elif data.startswith('lang_') and data[5:] in LANGUAGES:
        lang = data[5:]
        name = callback.get('from', {}).get('first_name', 'friend').replace('{', '').replace('}', '')
        text, menu = LANGUAGES[lang]['title'].format(name=name), info_menu(lang)
    elif data.startswith(('card_', 'crypto_')):
        method, _, lang = data.partition('_')
        if lang not in LANGUAGES:
            return
        text = LANGUAGES[lang]['card_info' if method == 'card' else 'crypto_info']
        menu = payment_menu(lang, method)
    else:
        return
    tg('editMessageText', {'chat_id': chat_id, 'message_id': message_id, 'text': text, 'reply_markup': menu})


@app.get('/')
def health():
    return jsonify({'status': 'running'}), 200


@app.post('/')
def webhook():
    if not BOT_TOKEN or not WEBHOOK_SECRET:
        logger.error('BOT_TOKEN or WEBHOOK_SECRET missing')
        return jsonify({'error': 'server not configured'}), 503
    if request.headers.get('X-Telegram-Bot-Api-Secret-Token') != WEBHOOK_SECRET:
        return jsonify({'error': 'unauthorized'}), 403
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'error': 'invalid JSON'}), 400
    try:
        handle_update(data)
    except Exception:
        logger.exception('Unhandled update error')
        return jsonify({'error': 'internal error'}), 500
    return jsonify({'ok': True}), 200
