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
    rows.append([{'text': t['demo'], 'callback_data': 'demo_' + lang}])
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
    # Only the configured administrator can ask for a video file_id.
    sender = message.get('from', {})
    is_admin = (bool(ADMIN_USERNAME) and
                sender.get('username', '').casefold() == ADMIN_USERNAME.casefold())
    video = message.get('video')
    if video and message.get('chat', {}).get('type') == 'private' and is_admin:
        tg('sendMessage', {
            'chat_id': message['chat']['id'],
            'text': 'VIDEO FILE ID:\n' + video['file_id']
        })
        return
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
    if data.startswith('demo_') and data[5:] in LANGUAGES:
        lang = data[5:]
        if not DEMO_VIDEO:
            tg('sendMessage', {'chat_id': chat_id,
                               'text': '🎬 Demo video is being updated. Please check back soon.'})
            return
        video_result = tg('sendVideo', {
            'chat_id': chat_id,
            'video': DEMO_VIDEO,
            'caption': '🎬 Premium channel preview',
            'supports_streaming': True,
            'reply_markup': {'inline_keyboard': [
                [{'text': LANGUAGES[lang]['card'], 'callback_data': 'card_' + lang}],
                [{'text': LANGUAGES[lang]['crypto'], 'callback_data': 'crypto_' + lang}],
                [{'text': LANGUAGES[lang]['back'], 'callback_data': 'lang_' + lang}]
            ]}
        })
        if not video_result.get('ok'):
            tg('sendMessage', {'chat_id': chat_id,
                               'text': 'Video is temporarily unavailable. Please try again later.'})
        return
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
    # Video messages have a caption, not editable text.
    # Use editMessageCaption for video callbacks so payment/back buttons work.
    if msg.get('video') or msg.get('animation') or msg.get('photo'):
        result = tg('editMessageCaption', {
            'chat_id': chat_id,
            'message_id': message_id,
            'caption': text,
            'reply_markup': menu
        })
    else:
        result = tg('editMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': text,
            'reply_markup': menu
        })

    # Fallback for messages Telegram does not permit editing.
    if not result.get('ok'):
        tg('sendMessage', {
            'chat_id': chat_id,
            'text': text,
            'reply_markup': menu
        })


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
