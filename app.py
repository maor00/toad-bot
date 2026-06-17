import os
import logging
import random
import asyncio
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- КАРТИНКИ ЖАБ (РАБОТАЮТ 100%) ---
TOAD_IMAGES = [
    "https://cdn.pixabay.com/photo/2016/03/31/19/02/frog-1295897_1280.png",
    "https://cdn.pixabay.com/photo/2017/05/30/09/27/frog-2356740_1280.jpg",
    "https://cdn.pixabay.com/photo/2020/07/28/21/37/frog-5446257_1280.jpg",
    "https://cdn.pixabay.com/photo/2019/03/31/09/50/frog-4093116_1280.jpg",
    "https://cdn.pixabay.com/photo/2018/10/02/11/01/frog-3718321_1280.jpg",
    "https://cdn.pixabay.com/photo/2017/09/05/14/06/frog-2718072_1280.jpg",
    "https://cdn.pixabay.com/photo/2018/07/13/21/44/frog-3536812_1280.jpg",
    "https://cdn.pixabay.com/photo/2016/09/06/15/57/frog-1647854_1280.jpg",
]

# --- Функции бота ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("🐸 Какая я сегодня жаба?", callback_data='get_toad')],
        [InlineKeyboardButton("ℹ️ О боте", callback_data='about')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"Привет, {user.first_name}! 👋\n\n"
        "Я - волшебный бот, который покажет тебе случайную жабу! 🐸\n\n"
        "Нажми на кнопку ниже!",
        reply_markup=reply_markup
    )

async def get_toad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()
        chat_id = query.message.chat_id
        await query.edit_message_reply_markup(reply_markup=None)
    else:
        chat_id = update.effective_chat.id
    
    toad_image = random.choice(TOAD_IMAGES)
    
    await context.bot.send_photo(
        chat_id=chat_id,
        photo=toad_image
    )
    
    keyboard = [[InlineKeyboardButton("🔄 Показать ещё", callback_data='get_toad')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=chat_id,
        text="Хочешь ещё жабу? Нажми на кнопку! 👇",
        reply_markup=reply_markup
    )

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    text = (
        "🐸 *О боте* 🐸\n\n"
        "Этот бот показывает случайные картинки с жабами!\n"
        "Каждый раз — новая жаба!\n\n"
        "💡 *Как использовать:*\n"
        "- Нажми 'Какая я сегодня жаба?'\n"
        "- Получи картинку\n"
        "- Делись с друзьями!\n\n"
        "🚀 *Команды:*\n"
        "/start - Главное меню\n"
        "/toad - Получить жабу\n"
        "/about - Информация о боте"
    )
    
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data='back_to_menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🐸 Какая я сегодня жаба?", callback_data='get_toad')],
        [InlineKeyboardButton("ℹ️ О боте", callback_data='about')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text="🐸 *Главное меню*\n\nВыбери действие:",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

# --- Запуск бота ---
async def run_bot():
    token = os.environ.get("TELEGRAM_TOKEN")
    if not token:
        logger.error("TELEGRAM_TOKEN не найден! Установите переменную окружения.")
        return
    
    application = Application.builder().token(token).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(get_toad, pattern='^get_toad$'))
    application.add_handler(CallbackQueryHandler(about, pattern='^about$'))
    application.add_handler(CallbackQueryHandler(back_to_menu, pattern='^back_to_menu$'))
    
    logger.info("Бот запускается...")
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    while True:
        await asyncio.sleep(1)

# --- Flask веб-сервер для Render ---
app = Flask(__name__)

@app.route('/')
def home():
    return "🐸 Бот с жабами работает!"

@app.route('/health')
def health():
    return "OK", 200

# --- Запуск всего вместе ---
if __name__ == "__main__":
    import threading
    
    def run_bot_thread():
        asyncio.run(run_bot())
    
    bot_thread = threading.Thread(target=run_bot_thread)
    bot_thread.start()
    
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Запуск веб-сервера на порту {port}")
    app.run(host='0.0.0.0', port=port)
