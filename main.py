import json
import logging
import os
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, jsonify, request
import requests

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('telegram-bot')

BOT_TOKEN = os.environ.get('BOT_TOKEN', '').strip()
WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET', '').strip()
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', '').strip().lstrip('@')
ADMIN_USER_ID = os.environ.get('ADMIN_USER_ID', '').strip()
DEMO_VIDEO = os.environ.get('DEMO_VIDEO_FILE_ID', '').strip() or os.environ.get('DEMO_VIDEO_URL', '').strip()
WELCOME_VIDEO = os.environ.get('WELCOME_VIDEO_FILE_ID', '').strip() or DEMO_VIDEO
UPSTASH_REDIS_REST_URL = os.environ.get('UPSTASH_REDIS_REST_URL', '').strip().rstrip('/')
UPSTASH_REDIS_REST_TOKEN = os.environ.get('UPSTASH_REDIS_REST_TOKEN', '').strip()
API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}'
SESSION = requests.Session()
FEEDBACK_KEY = 'lustheven:feedback:photos'
FEEDBACK_STAGE_PREFIX = 'lustheven:feedback:stage:'
FEEDBACK_SENT_PREFIX = 'lustheven:feedback:sent:'

LANGUAGES = {
    'en': {
        'title': (
            "**Hello, {name} 👋**\n\n"
            "In the premium channel, you will find exclusive content along with regular updates.\n\n"
            "**For a one-time fee of $20 (a single payment for lifetime access), you will gain entry to 3 groups containing over 50,000 videos; backup groups are also included.**\n\n"
            "_Group 1: Leaked content from OnlyFans, featuring popular and trending creators from the platform._\n"
            "_Group 2: Leaked content involving couples from various countries._\n"
            "_Group 3: Content featuring young women (over 18) — including masturbation scenes, webcam sessions, and Omegle-style interactions._"
        ),
        'demo': '🎬 View demo', 'feedback': '⭐ Customer Feedback',
        'feedback_intro': '⭐ Customer Feedback\n\nReal feedback shared by our customers. Thank you for your trust!',
        'feedback_empty': 'Customer feedback is being updated. Please check back soon.',
        'card': '💳 Card / Apple Pay', 'crypto': '💠 Crypto', 'back': '⬅️ Back',
        'card_info': 'Contact our manager to request card payment instructions.',
        'crypto_info': 'Contact our manager to request cryptocurrency payment instructions.',
        'contact': '✉️ Contact manager',
        'invoice': 'Hello! I would like to request payment instructions for lifetime access by card.',
        'crypto_request': 'Hello! I would like to request payment instructions for lifetime access by crypto.'
    },
    'es': {
        'title': (
            "**¡Hola, {name} 👋**\n\n"
            "En el canal premium encontrarás contenido exclusivo junto con actualizaciones periódicas.\n\n"
            "**Por una tarifa única de $20 (un solo pago para acceso de por vida), obtendrás acceso a 3 grupos que contienen más de 50.000 vídeos; también se incluyen grupos de respaldo.**\n\n"
            "_Grupo 1: Contenido filtrado de OnlyFans, con creadores populares y en tendencia de la plataforma._\n"
            "_Grupo 2: Contenido filtrado de parejas de varios países._\n"
            "_Grupo 3: Contenido con mujeres jóvenes (mayores de 18 años), incluyendo escenas de masturbación, sesiones de cámara web e interacciones estilo Omegle._"
        ),
        'demo': '🎬 Ver demostración', 'feedback': '⭐ Opiniones de clientes',
        'feedback_intro': '⭐ Opiniones de clientes\n\nOpiniones reales compartidas por nuestros clientes. ¡Gracias por confiar en nosotros!',
        'feedback_empty': 'Estamos actualizando las opiniones de clientes. Vuelve pronto.',
        'card': '💳 Tarjeta / Apple Pay', 'crypto': '💠 Cripto', 'back': '⬅️ Volver',
        'card_info': 'Contacta al administrador para solicitar instrucciones de pago con tarjeta.',
        'crypto_info': 'Contacta al administrador para solicitar instrucciones de pago con criptomonedas.',
        'contact': '✉️ Contactar al administrador',
        'invoice': 'Hola. Quiero solicitar instrucciones de pago con tarjeta.',
        'crypto_request': 'Hola. Quiero solicitar instrucciones de pago con criptomonedas.'
    },
    'fr': {
        'title': (
            "**Bonjour, {name} 👋**\n\n"
            "Dans la chaîne premium, vous trouverez du contenu exclusif ainsi que des mises à jour régulières.\n\n"
            "**Pour un tarif unique de 20 $ (un seul paiement pour un accès à vie), vous obtiendrez l'accès à 3 groupes contenant plus de 50 000 vidéos ; des groupes de sauvegarde sont également inclus.**\n\n"
            "_Groupe 1 : Contenu divulgué d'OnlyFans, mettant en vedette des créateurs populaires et tendance de la plateforme._\n"
            "_Groupe 2 : Contenu divulgué impliquant des couples de divers pays._\n"
            "_Groupe 3 : Contenu mettant en vedette des jeunes femmes (de plus de 18 ans) — comprenant des scènes de masturbation, des sessions webcam et des interactions de style Omegle._"
        ),
        'demo': '🎬 Voir la démo', 'feedback': '⭐ Avis clients',
        'feedback_intro': '⭐ Avis clients\n\nDécouvrez les avis partagés par nos clients. Merci pour votre confiance !',
        'feedback_empty': 'Les avis clients sont en cours de mise à jour. Revenez bientôt.',
        'card': '💳 Carte / Apple Pay', 'crypto': '💠 Crypto', 'back': '⬅️ Retour',
        'card_info': 'Contactez notre responsable pour obtenir les instructions de paiement par carte.',
        'crypto_info': 'Contactez notre responsable pour obtenir les instructions de paiement en cryptomonnaie.',
        'contact': '✉️ Contacter le responsable',
        'invoice': 'Bonjour ! Je souhaite recevoir les instructions de paiement par carte.',
        'crypto_request': 'Bonjour ! Je souhaite recevoir les instructions de paiement en cryptomonnaie.'
    },
    'pt': {
        'title': (
            "**Olá, {name} 👋**\n\n"
            "No canal premium, você encontrará conteúdo exclusivo junto com atualizações regulares.\n\n"
            "**Por uma taxa única de $20 (um pagamento único para acesso vitalício), você terá acesso a 3 grupos contendo mais de 50.000 vídeos; grupos de backup também estão incluídos.**\n\n"
            "_Grupo 1: Conteúdo vazado do OnlyFans, apresentando criadores populares e em alta na plataforma._\n"
            "_Grupo 2: Conteúdo vazado envolvendo casais de vários países._\n"
            "_Grupo 3: Conteúdo com mulheres jovens (maiores de 18 anos) — incluindo cenas de masturbação, sessões de webcam e interações no estilo Omegle._"
        ),
        'demo': '🎬 Ver demonstração', 'feedback': '⭐ Avaliações de clientes',
        'feedback_intro': '⭐ Avaliações de clientes\n\nVeja avaliações compartilhadas por nossos clientes. Obrigado pela confiança!',
        'feedback_empty': 'As avaliações dos clientes estão sendo atualizadas. Volte em breve.',
        'card': '💳 Cartão / Apple Pay', 'crypto': '💠 Cripto', 'back': '⬅️ Voltar',
        'card_info': 'Entre em contato com o administrador para obter instruções de pagamento com cartão.',
        'crypto_info': 'Entre em contato com o administrador para obter instruções de pagamento com criptomoedas.',
        'contact': '✉️ Falar com o administrador',
        'invoice': 'Olá! Gostaria de receber instruções de pagamento por cartão.',
        'crypto_request': 'Olá! Gostaria de receber instruções de pagamento por cripto.'
    }
}


def tg(method, payload):
    if not BOT_TOKEN:
        return {'ok': False}
    try:
        response = SESSION.post(f'{API_URL}/{method}', json=payload, timeout=15)
        response.raise_for_status()
        result = response.json()
        if not result.get('ok'):
            logger.error('Telegram API %s: %s', method, result.get('description', 'unknown error'))
        return result
    except (requests.RequestException, ValueError) as exc:
        logger.error('Telegram request %s failed: %s', method, type(exc).__name__)
        return {'ok': False}


def redis_command(*parts):
    if not UPSTASH_REDIS_REST_URL or not UPSTASH_REDIS_REST_TOKEN:
        raise RuntimeError('Upstash Redis is not configured')
    response = SESSION.post(
        UPSTASH_REDIS_REST_URL,
        json=list(parts),
        headers={'Authorization': f'Bearer {UPSTASH_REDIS_REST_TOKEN}'},
        timeout=10
    )
    response.raise_for_status()
    body = response.json()
    if body.get('error'):
        raise RuntimeError(body['error'])
    return body.get('result')


def redis_get_json(key, default):
    value = redis_command('GET', key)
    return json.loads(value) if value else default


def redis_set_json(key, value):
    redis_command('SET', key, json.dumps(value, ensure_ascii=False))


def is_admin(sender, chat):
    if chat.get('type') != 'private':
        return False
    if ADMIN_USER_ID:
        return str(sender.get('id', '')) == ADMIN_USER_ID
    return bool(ADMIN_USERNAME) and sender.get('username', '').casefold() == ADMIN_USERNAME.casefold()


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
    return {'inline_keyboard': [
        [{'text': t['demo'], 'callback_data': 'demo_' + lang}],
        [{'text': t['feedback'], 'callback_data': 'feedback_' + lang}],
        [{'text': t['card'], 'callback_data': 'card_' + lang}],
        [{'text': t['crypto'], 'callback_data': 'crypto_' + lang}],
        [{'text': t['back'], 'callback_data': 'back_languages'}]
    ]}


def payment_menu(lang, method):
    t = LANGUAGES[lang]
    msg = t['invoice'] if method == 'card' else t['crypto_request']
    rows = []
    url = manager_url(msg)
    if url:
        rows.append([{'text': t['contact'], 'url': url}])
    rows.append([{'text': t['back'], 'callback_data': 'lang_' + lang}])
    return {'inline_keyboard': rows}


def replace_screen(chat_id, old_message_id, method, payload):
    # Nếu dùng Markdown (để in đậm/in nghiêng), thêm parse_mode='Markdown' vào payload nếu chưa có
    payload.setdefault('parse_mode', 'Markdown')
    result = tg(method, dict(payload, chat_id=chat_id))
    if result.get('ok'):
        tg('deleteMessage', {'chat_id': chat_id, 'message_id': old_message_id})
    return result


def demo_keyboard(lang):
    t = LANGUAGES[lang]
    return {'inline_keyboard': [
        [{'text': t['feedback'], 'callback_data': 'feedback_' + lang}],
        [{'text': t['card'], 'callback_data': 'vcard_' + lang}],
        [{'text': t['crypto'], 'callback_data': 'vcrypto_' + lang}],
        [{'text': t['back'], 'callback_data': 'lang_' + lang}]
    ]}


def admin_reply(chat_id, text):
    tg('sendMessage', {'chat_id': chat_id, 'text': text})


def handle_admin_message(message, sender, chat):
    chat_id = chat['id']
    text = (message.get('text') or '').strip()
    if text.startswith('/addfeedback'):
        redis_set_json(FEEDBACK_STAGE_PREFIX + str(sender['id']), [])
        admin_reply(chat_id, 'Đã bắt đầu nhận feedback. Bạn gửi ảnh hoặc album ảnh, sau đó gửi /done để lưu.')
        return True
    if text.startswith('/done'):
        staged = redis_get_json(FEEDBACK_STAGE_PREFIX + str(sender['id']), None)
        if staged is None:
            admin_reply(chat_id, 'Bạn chưa bắt đầu thêm ảnh. Gửi /addfeedback trước nhé.')
            return True
        if staged:
            current = redis_get_json(FEEDBACK_KEY, [])
            current.extend(staged)
            redis_set_json(FEEDBACK_KEY, current)
        redis_command('DEL', FEEDBACK_STAGE_PREFIX + str(sender['id']))
        admin_reply(chat_id, f'Đã lưu {len(staged)} ảnh feedback. Tổng hiện tại: {len(redis_get_json(FEEDBACK_KEY, []))} ảnh.')
        return True
    if text.startswith('/listfeedback'):
        items = redis_get_json(FEEDBACK_KEY, [])
        admin_reply(chat_id, f'Hiện có {len(items)} ảnh feedback đã lưu.')
        return True
    if text.startswith('/clearfeedback'):
        redis_command('DEL', FEEDBACK_KEY)
        admin_reply(chat_id, 'Đã xóa toàn bộ ảnh feedback đã lưu.')
        return True

    photo = message.get('photo')
    if photo:
        stage_key = FEEDBACK_STAGE_PREFIX + str(sender['id'])
        staged = redis_get_json(stage_key, None)
        if staged is not None:
            file_id = photo[-1]['file_id']
            if file_id not in staged:
                staged.append(file_id)
                redis_set_json(stage_key, staged)
            return True
    if message.get('video'):
        admin_reply(chat_id, 'DEMO VIDEO FILE ID:\n' + message['video']['file_id'])
        return True
    return False


def cleanup_feedback_messages(chat_id):
    key = FEEDBACK_SENT_PREFIX + str(chat_id)
    try:
        message_ids = redis_get_json(key, [])
        if message_ids:
            redis_command('DEL', key)
    except Exception:
        logger.exception('Could not read/clear sent feedback message IDs')
        return

    if not message_ids:
        return

    def delete_one(message_id):
        return tg('deleteMessage', {
            'chat_id': chat_id,
            'message_id': message_id
        })

    with ThreadPoolExecutor(max_workers=min(10, len(message_ids))) as executor:
        list(executor.map(delete_one, message_ids))


def send_feedback(chat_id, old_message_id, lang):
    t = LANGUAGES[lang]
    try:
        photos = redis_get_json(FEEDBACK_KEY, [])
    except Exception:
        logger.exception('Could not read feedback from Redis')
        tg('sendMessage', {'chat_id': chat_id, 'text': 'Feedback is temporarily unavailable. Please try again later.'})
        return

    if not photos:
        result = tg('sendMessage', {
            'chat_id': chat_id,
            'text': t['feedback_empty'],
            'reply_markup': {'inline_keyboard': [[{'text': t['back'], 'callback_data': 'lang_' + lang}]]}
        })
        if result.get('ok'):
            tg('deleteMessage', {'chat_id': chat_id, 'message_id': old_message_id})
        return

    sent_message_ids = []
    for start in range(0, len(photos), 10):
        batch = photos[start:start + 10]
        if len(batch) == 1:
            result = tg('sendPhoto', {'chat_id': chat_id, 'photo': batch[0]})
            if result.get('ok'):
                sent_message_ids.append(result.get('result', {}).get('message_id'))
        else:
            media = [{'type': 'photo', 'media': file_id} for file_id in batch]
            result = tg('sendMediaGroup', {'chat_id': chat_id, 'media': media})
            if result.get('ok'):
                sent_message_ids.extend(
                    item.get('message_id') for item in result.get('result', [])
                    if item.get('message_id') is not None
                )
        if not result.get('ok'):
            logger.error('Could not send feedback album')
            if not sent_message_ids:
                return

    if sent_message_ids:
        try:
            redis_set_json(FEEDBACK_SENT_PREFIX + str(chat_id), sent_message_ids)
        except Exception:
            logger.exception('Could not save sent feedback message IDs')

    screen = tg('sendMessage', {
        'chat_id': chat_id,
        'text': t['feedback_intro'],
        'reply_markup': {'inline_keyboard': [[{'text': t['back'], 'callback_data': 'lang_' + lang}]]}
    })
    if screen.get('ok'):
        tg('deleteMessage', {'chat_id': chat_id, 'message_id': old_message_id})


def handle_update(update):
    message = update.get('message') or {}
    sender = message.get('from') or {}
    chat = message.get('chat') or {}

    if message and is_admin(sender, chat):
        try:
            if handle_admin_message(message, sender, chat):
                return
        except Exception:
            logger.exception('Admin feedback command failed')
            admin_reply(chat['id'], 'Có lỗi khi xử lý. Kiểm tra cấu hình Redis trên Vercel nhé.')
            return

    if message.get('text', '').split(' ', 1)[0].split('@')[0] == '/start':
        tg('sendMessage', {
            'chat_id': chat['id'],
            'text': '🌐 Choose your language / Selecciona tu idioma',
            'reply_markup': language_menu()
        })
        return

    callback = update.get('callback_query')
    if not callback:
        return
    cb_id = callback.get('id')
    if cb_id:
        tg('answerCallbackQuery', {'callback_query_id': cb_id})

    msg = callback.get('message') or {}
    if not msg.get('chat') or not msg.get('message_id'):
        return
    chat_id = msg['chat']['id']
    message_id = msg['message_id']
    data = callback.get('data', '')

    cleanup_feedback_messages(chat_id)

    if data.startswith('demo_') and data[5:] in LANGUAGES:
        lang = data[5:]
        if not DEMO_VIDEO:
            tg('answerCallbackQuery', {'callback_query_id': cb_id, 'text': 'Demo video is not configured.', 'show_alert': True})
            return
        replace_screen(chat_id, message_id, 'sendVideo', {
            'video': DEMO_VIDEO, 'caption': '🎬 Premium channel preview',
            'supports_streaming': True, 'reply_markup': demo_keyboard(lang)
        })
        return

    if data.startswith('feedback_') and data[9:] in LANGUAGES:
        send_feedback(chat_id, message_id, data[9:])
        return

    if data == 'back_languages':
        text = '🌐 Choose your language / Selecciona tu idioma'
        menu = language_menu()
    elif data.startswith('lang_') and data[5:] in LANGUAGES:
        lang = data[5:]
        name = callback.get('from', {}).get('first_name', 'friend')
        name = name.replace('{', '').replace('}', '')
        text = LANGUAGES[lang]['title'].format(name=name)
        menu = info_menu(lang)
    elif data.startswith(('vcard_', 'vcrypto_', 'card_', 'crypto_')):
        from_demo = data.startswith('v')
        clean = data[1:] if from_demo else data
        method, _, lang = clean.partition('_')
        if lang not in LANGUAGES:
            return
        t = LANGUAGES[lang]
        text = t['card_info'] if method == 'card' else t['crypto_info']
        menu = payment_menu(lang, method)
        if from_demo:
            menu['inline_keyboard'][-1][0]['callback_data'] = 'demo_' + lang
    else:
        return

    if data.startswith('lang_') and data[5:] in LANGUAGES and WELCOME_VIDEO:
        replace_screen(chat_id, message_id, 'sendVideo', {
            'video': WELCOME_VIDEO,
            'caption': text,
            'supports_streaming': True,
            'parse_mode': 'Markdown',
            'reply_markup': menu
        })
    else:
        replace_screen(chat_id, message_id, 'sendMessage', {
            'text': text,
            'parse_mode': 'Markdown',
            'reply_markup': menu
        })


@app.get('/')
def health():
    return jsonify({'status': 'running', 'feedback': 'enabled'}), 200


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
