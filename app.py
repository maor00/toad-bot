import os
import logging
import random
import asyncio
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Список для хранения file_id картинок
TOAD_IMAGES = []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [[InlineKeyboardButton("🐸 Какая я сегодня жаба?", callback_data='get_toad')],
                [InlineKeyboardButton("ℹ️ О боте", callback_data='about')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"Привет, {user.first_name}! 👋\n\nЯ покажу тебе случайную жабу! 🐸\n\n"
        "📸 Чтобы добавить свои картинки, просто отправь мне фото!\n"
        "Нажми на кнопку ниже, чтобы получить жабу!",
        reply_markup=reply_markup
    )

async def add_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохраняем file_id отправленных картинок"""
    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        if file_id not in TOAD_IMAGES:
            TOAD_IMAGES.append(file_id)
            await update.message.reply_text(f"✅ Картинка добавлена! Всего {len(TOAD_IMAGES)} картинок.")
            logger.info(f"Добавлена картинка: {file_id}")
        else:
            await update.message.reply_text("⚠️ Такая картинка уже есть!")

async def get_toad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()
        chat_id = query.message.chat_id
        await query.edit_message_reply_markup(reply_markup=None)
    else:
        chat_id = update.effective_chat.id
    
    if not TOAD_IMAGES:
        await context.bot.send_message(
            chat_id=chat_id,
            text="😅 Нет картинок! Отправь мне хотя бы одно фото жабы!"
        )
        return
    
    toad_image = random.choice(TOAD_IMAGES)
    await context.bot.send_photo(chat_id=chat_id, photo=toad_image)
    
    keyboard = [[InlineKeyboardButton("🔄 Показать ещё", callback_data='get_toad')]]
    await context.bot.send_message(
        chat_id=chat_id,
        text="Хочешь ещё жабу? Нажми на кнопку! 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = (
        "🐸 *О боте* 🐸\n\nЭтот бот показывает случайные картинки с жабами!\n\n"
        "📸 *Как добавить свои картинки:*\nПросто отправь мне фото жабы!\n\n"
        "🚀 *Команды:*\n/start - Главное меню\n/toad - Получить жабу\n/about - О боте"
    )
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data='back_to_menu')]]
    await query.edit_message_text(text=text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🐸 Какая я сегодня жаба?", callback_data='get_toad')],
        [InlineKeyboardButton("ℹ️ О боте", callback_data='about')]
    ]
    await query.edit_message_text(
        text="🐸 *Главное меню*\n\nВыбери действие:",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def run_bot():
    token = os.environ.get("TELEGRAM_TOKEN")
    if not token:
        logger.error("TELEGRAM_TOKEN не найден!")
        return
    
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("toad", get_toad))
    application.add_handler(CallbackQueryHandler(get_toad, pattern='^get_toad$'))
    application.add_handler(CallbackQueryHandler(about, pattern='^about$'))
    application.add_handler(CallbackQueryHandler(back_to_menu, pattern='^back_to_menu$'))
    application.add_handler(MessageHandler(filters.PHOTO, add_image))
    
    logger.info("Бот запускается...")
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    while True:
        await asyncio.sleep(1)

app = Flask(__name__)

@app.route('/')
def home():
    return "🐸 Бот с жабами работает!"

@app.route('/health')
def health():
    return "OK", 200

if __name__ == "__main__":
    import threading
    threading.Thread(target=lambda: asyncio.run(run_bot())).start()
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Запуск веб-сервера на порту {port}")
    app.run(host='0.0.0.0', port=port)
