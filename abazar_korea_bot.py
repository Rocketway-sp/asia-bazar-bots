import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)

# --- НАСТРОЙКИ ---
BOT_TOKEN = "8904735821:AAFSloXROv1dN_6VPcGk_77pHDmuDVV5znE"
MANAGER_ID = 8646658010

# --- ШАГИ ДИАЛОГА ---
BUDGET, BODY, COUNTRY, CITY, CONTACT = range(5)

logging.basicConfig(level=logging.INFO)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["🚗 Да, начнём!"]]
    await update.message.reply_text(
        "👋 Привет! Я сделаю заявку на консультацию по авто из Азии. Это займёт 2 минуты. Поехали?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return BUDGET


async def budget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["до 1.5 млн", "1.5 — 2.5 млн"],
        ["2.5 — 4 млн", "от 4 млн"]
    ]
    await update.message.reply_text(
        "💰 Какой у тебя бюджет?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return BUDGET


async def get_budget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["budget"] = update.message.text
    await update.message.reply_text(
        "🚙 Какую машину или кузов рассматриваешь?",
        reply_markup=ReplyKeyboardRemove()
    )
    return BODY


async def get_body(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["body"] = update.message.text
    keyboard = [
        ["🇰🇷 Корея", "🇨🇳 Китай"],
        ["Любая Азия"]
    ]
    await update.message.reply_text(
        "🌏 Откуда везём авто?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return COUNTRY


async def get_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["country"] = update.message.text
    await update.message.reply_text(
        "📍 В какой город доставляем?",
        reply_markup=ReplyKeyboardRemove()
    )
    return CITY


async def get_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["city"] = update.message.text
    await update.message.reply_text(
        "📱 Отлично! Последний шаг — напиши своё имя / @тг и номер телефона."
    )
    return CONTACT


async def get_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["contact"] = update.message.text
    user = update.message.from_user

    # Сообщение менеджеру
    manager_text = (
        "🚗 *Новая заявка с бота!*\n\n"
        f"💰 Бюджет: {context.user_data['budget']}\n"
        f"🚙 Авто/кузов: {context.user_data['body']}\n"
        f"🌏 Страна: {context.user_data['country']}\n"
        f"📍 Город: {context.user_data['city']}\n"
        f"📱 Контакт: {context.user_data['contact']}\n\n"
        f"👤 Telegram: @{user.username or 'нет'} (ID: {user.id})"
    )

    await context.bot.send_message(
        chat_id=MANAGER_ID,
        text=manager_text,
        parse_mode="Markdown"
    )

    # Ответ клиенту
    await update.message.reply_text(
        "✅ Отлично! Заявка принята. Менеджер свяжется с тобой в ближайшее время.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Окей, если передумаешь — просто напиши /start 🚗",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            BUDGET: [
                MessageHandler(filters.Regex("^🚗 Да, начнём!$"), budget),
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_budget),
            ],
            BODY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_body)],
            COUNTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_country)],
            CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_city)],
            CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_contact)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv)
    print("✅ Бот запущен! Нажми Ctrl+C чтобы остановить.")
    app.run_polling()


if __name__ == "__main__":
    main()
