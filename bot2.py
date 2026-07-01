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

def log_step(user, step, detail=""):
    username = f"@{user.username}" if user.username else f"id:{user.id}"
    name = user.full_name or "—"
    msg = f"[BOT2] {username} ({name}) | шаг: {step}"
    if detail:
        msg += f" | {detail}"
    logger.info(msg)

async def start(update, context):
    user = update.message.from_user
    log_step(user, "ОТКРЫЛ БОТА")
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
    user = query.from_user
    await query.answer()
    log_step(user, "НАЧАЛ АНКЕТУ", "нажал Бесплатный подбор авто")
    keyboard = [["до 1.5 млн", "1.5 — 2.5 млн"], ["2.5 — 4 млн", "от 4 млн"]]
    await query.message.reply_text(
        "Отлично! Это займёт 2 минуты.\n\nКакой у вас бюджет?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    )
    return BUDGET

async def get_budget(update, context):
    user = update.message.from_user
    context.user_data["budget"] = update.message.text
    log_step(user, "ШАГ 1 БЮДЖЕТ", update.message.text)
    await update.message.reply_text(
        "Какой автомобиль или тип кузова вас интересует?",
        reply_markup=ReplyKeyboardRemove()
    )
    return BODY

async def get_body(update, context):
    user = update.message.from_user
    context.user_data["body"] = update.message.text
    log_step(user, "ШАГ 2 КУЗОВ", update.message.text)
    keyboard = [["Корея", "Китай"], ["Любая Азия"]]
    await update.message.reply_text(
        "Из какой страны будем везти автомобиль?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    )
    return COUNTRY

async def get_country(update, context):
    user = update.message.from_user
    context.user_data["country"] = update.message.text
    log_step(user, "ШАГ 3 СТРАНА", update.message.text)
    await update.message.reply_text(
        "В какой город доставляем?",
        reply_markup=ReplyKeyboardRemove()
    )
    return CITY

async def get_city(update, context):
    user = update.message.from_user
    context.user_data["city"] = update.message.text
    log_step(user, "ШАГ 4 ГОРОД", update.message.text)
    await update.message.reply_text("Представьтесь, пожалуйста. Введите имя и фамилию.")
    return NAME

async def get_name(update, context):
    user = update.message.from_user
    context.user_data["name"] = update.message.text
    log_step(user, "ШАГ 5 ИМЯ", update.message.text)
    await update.message.reply_text(
        "Введите номер телефона для связи в формате:\n+7XXXXXXXXXX или +8XXXXXXXXXX"
    )
    return PHONE

async def get_phone(update, context):
    user = update.message.from_user
    phone = update.message.text.strip()
    if not re.match(r'^\+[78]\d{10}$', phone):
        log_step(user, "ШАГ 6 ТЕЛЕФОН ОШИБКА", phone)
        await update.message.reply_text(
            "Неверный формат номера. Введите без пробелов:\n+7XXXXXXXXXX или +8XXXXXXXXXX\n\nПопробуйте ещё раз:"
        )
        return PHONE

    context.user_data["phone"] = phone
    log_step(user, "ШАГ 6 ТЕЛЕФОН — ЗАЯВКА ЗАВЕРШЕНА", phone)

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
    user = update.message.from_user
    log_step(user, "ОТМЕНИЛ АНКЕТУ")
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
