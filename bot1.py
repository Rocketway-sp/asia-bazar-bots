import logging
import re
from datetime import datetime
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ConversationHandler, CallbackQueryHandler
)
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

BOT_TOKEN = "8998156856:AAGBpncU7tpN5HOr9cyxZxRqO3RSnkD9p_o"
MANAGER_ID = 8646658010

BUDGET, BODY, COUNTRY, CITY, NAME, PHONE = range(6)

def log_step(user, step, detail=""):
    username = f"@{user.username}" if user.username else f"id:{user.id}"
    name = user.full_name or "—"
    msg = f"[BOT1] {username} ({name}) | шаг: {step}"
    if detail:
        msg += f" | {detail}"
    logger.info(msg)

async def start(update, context):
    user = update.message.from_user
    log_step(user, "ОТКРЫЛ БОТА")
    keyboard = [
        [InlineKeyboardButton("🚗 Бесплатный подбор авто", callback_data="apply")],
        [InlineKeyboardButton("📢 Наш канал с авто в наличии", url="https://t.me/asiabazarkr")],
        [InlineKeyboardButton("⭐️ Отзывы клиентов", url="https://t.me/asiabazarotzivi")],
        [InlineKeyboardButton("🌐 Наш сайт", url="https://asia-bazar-korea.com/")],
    ]
    with open("welcome.gif", "rb") as gif:
        await update.message.reply_animation(
            animation=gif,
            caption="👋 Привет! Я представляю ASIA BAZAR — пригон авто из Кореи и Китая под ключ.\n\nВыбери что тебя интересует 👇",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def apply_callback(update, context):
    query = update.callback_query
    user = query.from_user
    await query.answer()
    log_step(user, "НАЧАЛ АНКЕТУ", "нажал Бесплатный подбор авто")
    keyboard = [["до 1.5 млн", "1.5 — 2.5 млн"], ["2.5 — 4 млн", "от 4 млн"]]
    await query.message.reply_text(
        "Отлично! Это займёт 2 минуты.\n\n💰 Какой у тебя бюджет?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    )
    return BUDGET

async def get_budget(update, context):
    user = update.message.from_user
    context.user_data["budget"] = update.message.text
    log_step(user, "ШАГ 1 БЮДЖЕТ", update.message.text)
    await update.message.reply_text("🚙 Какую машину или кузов рассматриваешь?", reply_markup=ReplyKeyboardRemove())
    return BODY

async def get_body(update, context):
    user = update.message.from_user
    context.user_data["body"] = update.message.text
    log_step(user, "ШАГ 2 КУЗОВ", update.message.text)
    keyboard = [["🇰🇷 Корея", "🇨🇳 Китай"], ["Любая Азия"]]
    await update.message.reply_text("🌏 Откуда везём авто?", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True))
    return COUNTRY

async def get_country(update, context):
    user = update.message.from_user
    context.user_data["country"] = update.message.text
    log_step(user, "ШАГ 3 СТРАНА", update.message.text)
    await update.message.reply_text("📍 В какой город доставляем?", reply_markup=ReplyKeyboardRemove())
    return CITY

async def get_city(update, context):
    user = update.message.from_user
    context.user_data["city"] = update.message.text
    log_step(user, "ШАГ 4 ГОРОД", update.message.text)
    await update.message.reply_text("👤 Как тебя зовут? Введи имя и фамилию.")
    return NAME

async def get_name(update, context):
    user = update.message.from_user
    context.user_data["name"] = update.message.text
    log_step(user, "ШАГ 5 ИМЯ", update.message.text)
    await update.message.reply_text(
        "📱 Введи номер телефона без пробелов в формате:\n+7XXXXXXXXXX или +8XXXXXXXXXX"
    )
    return PHONE

async def get_phone(update, context):
    user = update.message.from_user
    phone = update.message.text.strip().replace(" ", '').replace("-", '')
    if not re.match(r'^\+[78]\d{10}$', phone):
        log_step(user, "ШАГ 6 ТЕЛЕФОН ОШИБКА", phone)
        await update.message.reply_text(
            "❌ Неверный формат. Введи номер без пробелов в формате:\n+7XXXXXXXXXX или +8XXXXXXXXXX\n\nПопробуй ещё раз:"
        )
        return PHONE

    context.user_data["phone"] = phone
    log_step(user, "ШАГ 6 ТЕЛЕФОН — ЗАЯВКА ЗАВЕРШЕНА", phone)

    manager_text = (
        "Новая заявка с бота!\n\n"
        f"💰 Бюджет: {context.user_data['budget']}\n"
        f"🚙 Авто/кузов: {context.user_data['body']}\n"
        f"🌏 Страна: {context.user_data['country']}\n"
        f"📍 Город: {context.user_data['city']}\n"
        f"👤 Имя: {context.user_data['name']}\n"
        f"📱 Телефон: {context.user_data['phone']}\n\n"
        f"Telegram: @{user.username or 'нет'} (ID: {user.id})"
    )
    await context.bot.send_message(chat_id=MANAGER_ID, text=manager_text)
    await update.message.reply_text(
        "✅ Заявка принята. Менеджер свяжется с тобой в ближайшее время.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

async def cancel(update, context):
    user = update.message.from_user
    log_step(user, "ОТМЕНИЛ АНКЕТУ")
    await update.message.reply_text("Окей, если передумаешь — просто напиши /start 🚗", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(apply_callback, pattern="^apply$")],
        states={
            BUDGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_budget)],
            BODY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_body)],
            COUNTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_country)],
            CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_city)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(conv)
    print("✅ Бот 1 запущен!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
