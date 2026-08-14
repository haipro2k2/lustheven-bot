import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Lấy cấu hình từ môi trường
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "")

TEXTS = {
    'vi': {
        'welcome': "👋 *Chào mừng bạn!*\nVui lòng chọn ngôn ngữ để tiếp tục:",
        'select_pkg': "📦 *Vui lòng chọn gói dịch vụ bạn muốn mua:*",
        'select_pay': "💳 *Bạn đã chọn:* {}\n\nVui lòng chọn phương thức thanh toán:",
        'invoice': "🧾 *HÓA ĐƠN ĐẶT HÀNG #{order_id}*\n\n"
                   "🔹 *Gói:* {pkg}\n"
                   "🔹 *Thanh toán:* {pay}\n"
                   "───────────────\n"
                   "👇 Nhấn nút bên dưới để nhắn tin trực tiếp với Admin và hoàn tất thanh toán!",
        'btn_chat': "💬 Chat với Admin ngay",
        'pkg_1m': "Gói 1 Tháng - $10",
        'pkg_1y': "Gói 1 Năm - $80",
        'pay_bank': "🏦 Ngân Hàng (VietQR)",
        'pay_crypto': "🪙 Crypto (USDT / TON)",
    },
    'en': {
        'welcome': "👋 *Welcome!*\nPlease select your language:",
        'select_pkg': "📦 *Please select the plan you want to purchase:*",
        'select_pay': "💳 *Selected:* {}\n\nPlease select a payment method:",
        'invoice': "🧾 *ORDER INVOICE #{order_id}*\n\n"
                   "🔹 *Plan:* {pkg}\n"
                   "🔹 *Payment:* {pay}\n"
                   "───────────────\n"
                   "👇 Click the button below to chat with Admin and complete payment!",
        'btn_chat': "💬 Chat with Admin Now",
        'pkg_1m': "1 Month Plan - $10",
        'pkg_1y': "1 Year Plan - $80",
        'pay_bank': "🏦 Bank Transfer",
        'pay_crypto': "🪙 Crypto (USDT / TON)",
    }
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🇻🇳 Tiếng Việt", callback_data='lang_vi'),
            InlineKeyboardButton("🇬🇧 English", callback_data='lang_en')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 *Chào mừng bạn / Welcome!*\nVui lòng chọn ngôn ngữ / Please select language:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith('lang_'):
        lang = 'vi' if data == 'lang_vi' else 'en'
        context.user_data['lang'] = lang
        t = TEXTS[lang]

        keyboard = [
            [InlineKeyboardButton(t['pkg_1m'], callback_data='pkg_1m')],
            [InlineKeyboardButton(t['pkg_1y'], callback_data='pkg_1y')]
        ]
        await query.edit_message_text(t['select_pkg'], reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    elif data.startswith('pkg_'):
        lang = context.user_data.get('lang', 'vi')
        t = TEXTS[lang]
        
        pkg_name = t['pkg_1m'] if data == 'pkg_1m' else t['pkg_1y']
        context.user_data['selected_pkg'] = pkg_name

        keyboard = [
            [InlineKeyboardButton(t['pay_bank'], callback_data='pay_bank')],
            [InlineKeyboardButton(t['pay_crypto'], callback_data='pay_crypto')]
        ]
        await query.edit_message_text(t['select_pay'].format(pkg_name), reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    elif data.startswith('pay_'):
        lang = context.user_data.get('lang', 'vi')
        t = TEXTS[lang]
        
        pay_method = t['pay_bank'] if data == 'pay_bank' else t['pay_crypto']
        pkg_name = context.user_data.get('selected_pkg', 'N/A')
        
        order_id = str(random.randint(10000, 99999))
        user = query.from_user
        username_str = f"@{user.username}" if user.username else f"ID: {user.id}"

        # Báo cho Admin
        admin_alert = (
            f"🚨 *ĐƠN HÀNG MỚI #{order_id}*\n"
            f"👤 Khách hàng: {user.full_name} ({username_str})\n"
            f"📦 Gói chọn: {pkg_name}\n"
            f"💳 PTTT: {pay_method}\n"
            f"🌐 Ngôn ngữ: {lang.upper()}"
        )
        if ADMIN_ID:
            try:
                await context.bot.send_message(chat_id=ADMIN_ID, text=admin_alert, parse_mode='Markdown')
            except Exception as e:
                print(f"Lỗi gửi thông báo Admin: {e}")

        # Trả về hóa đơn cho khách
        msg_text = t['invoice'].format(order_id=order_id, pkg=pkg_name, pay=pay_method)
        encoded_text = f"Xin chào, tôi muốn thanh toán đơn hàng #{order_id} ({pkg_name})"
        chat_url = f"https://t.me/{ADMIN_USERNAME}?text={encoded_text.replace(' ', '%20')}"
        
        keyboard = [[InlineKeyboardButton(t['btn_chat'], url=chat_url)]]
        await query.edit_message_text(msg_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_buttons))
    print("Bot đang chạy...")
    app.run_polling()
