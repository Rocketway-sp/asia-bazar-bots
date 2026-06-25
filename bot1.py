import logging
import re
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = "8998156856:AAGBpncU7tpN5HOr9cyxZxRqO3RSnkD9p_o"
MANAGER_ID = 8646658010

BUDGET, BODY, COUNTRY, CITY, NAME, PHONE = range(6)

async def start(update, context):
    keyboard = [["до 1.5 млн", "1.5 — 2.5 млн"], ["2.5 — 4 млн", "от 4 млн"]]
    await update.message.reply_text(
        "👋 Привет! Я сделаю заявку на консультацию по авто из Азии. Это займёт 2 минуты.\n\n💰 Какой у тебя бюджет?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    )
    return BUDGET

async def get_budget(update, context):
    context.user_data["budget"] = update.message.text
    await update.message.reply_text("🚙 Какую машину или кузов рассматриваешь?", reply_markup=ReplyKeyboardRemove())
    return BODY

async def get_body(update, context):
    context.user_data["body"] = update.message.text
    keyboard = [["🇰🇷 Корея", "🇨🇳 Китай"], ["Любая Азия"]]
    await update.message.reply_text("🌏 Откуда везём авто?", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True))
    return COUNTRY

async def get_country(update, context):
    context.user_data["country"] = update.message.text
    await update.message.reply_text("📍 В какой город доставляем?", reply_markup=ReplyKeyboardRemove())
    return CITY

async def get_city(update, context):
    context.user_data["city"] = update.message.text
    await update.message.reply_text("👤 Как тебя зовут? Введи имя и фамилию.")
    return NAME

async def get_name(update, context):
    context.user_data["name"] = update.message.text
    await update.message.reply_text(
        "📱 Введи номер телефона в формате:\n+7XXXXXXXXXX или +8XXXXXXXXXX"
    )
    return PHONE

async def get_phone(update, context):
    phone = update.message.text.strip()
    if not re.match(r'^\+[78]\d{10}$', phone):
        await update.message.reply_text(
            "❌ Неверный формат. Введи номер в формате:\n+7XXXXXXXXXX или +8XXXXXXXXXX\n\nПопробуй ещё раз:"
        )
        return PHONE

    context.user_data["phone"] = phone
    user = update.message.from_user
    manager_text = (
        "🚗 *Новая заявка с бота!*\n\n"
        f"💰 Бюджет: {context.user_data['budget']}\n"
        f"🚙 Авто/кузов: {context.user_data['body']}\n"
        f"🌏 Страна: {context.user_data['country']}\n"
        f"📍 Город: {context.user_data['city']}\n"
        f"👤 Имя: {context.user_data['name']}\n"
        f"📱 Телефон: {context.user_data['phone']}\n\n"
        f"Telegram: @{user.username or 'нет'} (ID: {user.id})"
    )
    await context.bot.send_message(chat_id=MANAGER_ID, text=manager_text, parse_mode="Markdown")
    await update.message.reply_text(
        "✅ Заявка принята. Менеджер свяжется с тобой в ближайшее время.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

async def cancel(update, context):
    await update.message.reply_text("Окей, если передумаешь — просто напиши /start 🚗", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
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
