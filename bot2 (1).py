import asyncio
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = "8655105931:AAFuw942uBa1eT7lQpkEskLsBZn4eb_ykXY"
MANAGER_ID = 8646658010

BUDGET, BODY, COUNTRY, CITY, CONTACT = range(5)

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
    await update.message.reply_text("📱 Последний шаг — напиши своё имя / @тг и номер телефона.")
    return CONTACT

async def get_contact(update, context):
    context.user_data["contact"] = update.message.text
    user = update.message.from_user
    manager_text = (
        "🚗 *Новая заявка с бота!*\n\n"
        f"💰 Бюджет: {context.user_data['budget']}\n"
        f"🚙 Авто/кузов: {context.user_data['body']}\n"
        f"🌏 Страна: {context.user_data['country']}\n"
        f"📍 Город: {context.user_data['city']}\n"
        f"📱 Контакт: {context.user_data['contact']}\n\n"
        f"👤 Telegram: @{user.username or 'нет'} (ID: {user.id})"
    )
    await context.bot.send_message(chat_id=MANAGER_ID, text=manager_text, parse_mode="Markdown")
    await update.message.reply_text("✅ Заявка принята. Менеджер свяжется с тобой в ближайшее время.", reply_markup=ReplyKeyboardRemove())
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
            CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_contact)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(conv)
    print("✅ Бот 2 запущен!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
