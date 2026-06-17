import os
import logging
import random
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Список определений "какая ты сегодня жаба"
TOAD_TYPES = [
    "🐸 Ты сегодня - Королевская жаба! Величественная и важная.",
    "🐸 Ты сегодня - Жаба-путешественница! Время открывать новые горизонты.",
    "🐸 Ты сегодня - Ленивая жаба на листе кувшинки. Отдыхай!",
    "🐸 Ты сегодня - Жаба-философ! Мудрость переполняет тебя.",
    "🐸 Ты сегодня - Прыгучая жаба! Энергия бьет ключом.",
    "🐸 Ты сегодня - Задумчивая жаба. Пора поразмышлять о важном.",
    "🐸 Ты сегодня - Крутая жаба в очках! Ты в тренде.",
    "🐸 Ты сегодня - Жаба-мечтатель! Витаешь в облаках.",
    "🐸 Ты сегодня - Коронованная жаба! Ты главный здесь.",
    "🐸 Ты сегодня - Жаба-спортсмен! Время для активности.",
    "🐸 Ты сегодня - Жаба-гурман! Наслаждайся вкусной едой.",
    "🐸 Ты сегодня - Жаба-артист! Твоя креативность безгранична.",
    "🐸 Ты сегодня - Сонная жаба. Выпей кофе!",
    "🐸 Ты сегодня - Жаба-дипломат! Решай конфликты грамотно.",
    "🐸 Ты сегодня - Золотая жаба! Удача на твоей стороне.",
    "🐸 Ты сегодня - Жаба-няшка! Ты просто прелесть.",
    "🐸 Ты сегодня - Боевая жаба! Готова к приключениям.",
    "🐸 Ты сегодня - Жаба-йог! Расслабление и гармония.",
    "🐸 Ты сегодня - Жаба-библиотекарь! Любишь тишину и книги.",
    "🐸 Ты сегодня - Жаба-стартап! Идеи переполняют тебя.",
]

# Ссылки на картинки жаб
TOAD_IMAGES = [
    "https://i.pinimg.com/564x/42/0d/9a/420d9a8642a318f01fcd5d455395349c.jpg",
    "https://i.pinimg.com/564x/db/fb/2b/dbfb2b23814cb8b19eb0b6677832e701.jpg",
    "https://i.pinimg.com/564x/4b/48/f1/4b48f12f12ce6cfc8919b4cdb718ede0.jpg",
    "https://i.pinimg.com/564x/1e/9f/4b/1e9f4b67d815976098afc5477729cf2f.jpg",
    "https://i.pinimg.com/564x/34/4b/1b/344b1b2db6db44813b383e08cb42d673.jpg",
    "https://i.pinimg.com/564x/03/19/15/031915ce81ad79f5f69761e8c2df8bce.jpg",
    "https://i.pinimg.com/564x/8f/da/0d/8fda0d4a7ae43dfc33344b0c0fcf2e54.jpg",
    "https://i.pinimg.com/564x/59/d8/64/59d864c2a7d824ba53778c8f5727099a.jpg",
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
        "Я - волшебный бот, который поможет тебе узнать, какая ты сегодня жаба! 🐸\n\n"
        "Нажми на кнопку ниже, чтобы получить своё жабо-определение и картинку!",
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
    
    toad_type = random.choice(TOAD_TYPES)
    toad_image = random.choice(TOAD_IMAGES)
    
    await context.bot.send_photo(
        chat_id=chat_id,
        photo=toad_image,
        caption=f"🐸 Твоя жаба на сегодня:\n\n{toad_type}"
    )
    
    keyboard = [[InlineKeyboardButton("🔄 Узнать снова", callback_data='get_toad')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=chat_id,
        text="Хочешь узнать ещё раз? Нажми на кнопку! 👇",
        reply_markup=reply_markup
    )

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    text = (
        "🐸 *О боте* 🐸\n\n"
        "Этот бот создан для хорошего настроения!\n"
        "Каждый раз он выбирает случайную жабу и показывает её картинку.\n\n"
        "💡 *Как использовать:*\n"
        "- Нажми 'Какая я сегодня жаба?'\n"
        "- Получи картинку и описание\n"
        "- Делись с друзьями!\n\n"
        "🚀 *Команды:*\n"
        "/start - Главное меню\n"
        "/toad - Узнать свою жабу\n"
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

# --- Запуск бота в отдельном потоке ---
def run_bot():
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
    application.run_polling()

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
    # Запускаем бота в отдельном потоке
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    
    # Запускаем Flask-сервер
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Запуск веб-сервера на порту {port}")
    app.run(host='0.0.0.0', port=port)
