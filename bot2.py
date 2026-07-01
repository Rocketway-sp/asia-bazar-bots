import logging
import re
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ConversationHandler, CallbackQueryHandler
)
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = "8655105931:AAFuw942uBa1eT7lQpkEskLsBZn4eb_ykXY"
MANAGER_ID = 8646658010

BUDGET, BODY, COUNTRY, CITY, NAME, PHONE = range(6)

WELCOME_TEXT = (
    "Добро пожаловать в ASIA BAZAR — официальный сервис пригона автомобилей из Кореи и Китая под ключ.\n\n"
    "5 лет мы помогаем клиентам по всей России выбрать и привезти автомобиль напрямую с азиатского рынка — "
    "без переплат дилерам, без скрытых комиссий и с полным сопровождением сделки.\n\n"
    "Что мы делаем:\n"
    "— Подбор автомобиля под ваш бюджет и запрос\n"
    "— Проверка истории и технического состояния\n"
    "— Выкуп, доставка и таможенное оформление\n"
    "— Постановка на учёт в России\n\n"
    "Выберите, что вас интересует:"
)

async def start(update, context):
    keyboard = [
        [InlineKeyboardButton("Бесплатный подбор авто", callback_data="apply")],
        [InlineKeyboardButton("Канал с авто в наличии", url="https://t.me/asiabazarkr")],
        [InlineKeyboardButton("Отзывы клиентов", url="https://t.me/asiabazarotzivi")],
        [InlineKeyboardButton("Наш сайт", url="https://asia-bazar-korea.com/")],
    ]
    await update.message.reply_text(
        WELCOME_TEXT,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def apply_callback(update, context):
    query = update.callback_query
    await query.answer()
    keyboard = [["до 1.5 млн", "1.5 — 2.5 млн"], ["2.5 — 4 млн", "от 4 млн"]]
    await query.message.reply_text(
        "Отлично! Это займёт 2 минуты.\n\nКакой у вас бюджет?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    )
    return BUDGET

async def get_budget(update, context):
    context.user_data["budget"] = update.message.text
    await update.message.reply_text(
        "Какой автомобиль или тип кузова вас интересует?",
        reply_markup=ReplyKeyboardRemove()
    )
    return BODY

async def get_body(update, context):
    context.user_data["body"] = update.message.text
    keyboard = [["Корея", "Китай"], ["Любая Азия"]]
    await update.message.reply_text(
        "Из какой страны будем везти автомобиль?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    )
    return COUNTRY

async def get_country(update, context):
    context.user_data["country"] = update.message.text
    await update.message.reply_text(
        "В какой город доставляем?",
        reply_markup=ReplyKeyboardRemove()
    )
    return CITY

async def get_city(update, context):
    context.user_data["city"] = update.message.text
    await update.message.reply_text("Представьтесь, пожалуйста. Введите имя и фамилию.")
    return NAME

async def get_name(update, context):
    context.user_data["name"] = update.message.text
    await update.message.reply_text(
        "Введите номер телефона для связи в формате:\n+7XXXXXXXXXX или +8XXXXXXXXXX"
    )
    return PHONE

async def get_phone(update, context):
    phone = update.message.text.strip()
    if not re.match(r'^\+[78]\d{10}$', phone):
        await update.message.reply_text(
            "Неверный формат номера. Введите без пробелов:\n+7XXXXXXXXXX или +8XXXXXXXXXX\n\nПопробуйте ещё раз:"
        )
        return PHONE

    context.user_data["phone"] = phone
    user = update.message.from_user
    manager_text = (
        "Новая заявка с бота!\n\n"
        f"Бюджет: {context.user_data['budget']}\n"
        f"Авто/кузов: {context.user_data['body']}\n"
        f"Страна: {context.user_data['country']}\n"
        f"Город: {context.user_data['city']}\n"
        f"Имя: {context.user_data['name']}\n"
        f"Телефон: {context.user_data['phone']}\n\n"
        f"Telegram: @{user.username or 'нет'} (ID: {user.id})"
    )
    await context.bot.send_message(chat_id=MANAGER_ID, text=manager_text)
    await update.message.reply_text(
        "Ваша заявка принята. Менеджер свяжется с вами в ближайшее время. Спасибо, что выбрали ASIA BAZAR.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

async def cancel(update, context):
    await update.message.reply_text(
        "Заявка отменена. Если захотите вернуться — напишите /start",
        reply_markup=ReplyKeyboardRemove()
    )
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
    print("Bot 2 started!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
