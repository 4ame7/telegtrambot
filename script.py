from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, KeyboardButton, InputFile
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, ContextTypes, filters
)
import logging
import datetime
import json
import os

# ======= НАСТРОЙКИ =========
BOT_TOKEN = "7739338057:AAHFzDpOgh-XrBr-vqWvV5TEqKs62HQS9zY"
CHANNEL_ID = -1002496521038
CHANNEL_LINK = "https://t.me/num_insight"
ADMIN_ID = 405069873
USERS_FILE = "users.json"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ======= STATES =======
ASK_BIRTHDATE = 0
SHOWING_KEYS = 1
NEW_POST_TEXT = 2
NEW_POST_IMAGE = 3
PREVIEW_POST = 4

# ======= Тексты для ключей =========
CONSCIOUSNESS_ENERGY_TEXTS = {i: f"Энергия сознания номер {i}: ты уникален!" for i in range(1, 23)}
MATERIAL_ENERGY_TEXTS = {i: f"Энергия материи номер {i}: стабильность и сила." for i in range(1, 10)}
SOUL_ENERGY_TEXTS = {i: f"Энергия души для месяца {i}: внутренний покой." for i in range(1, 13)}

ADDITIONAL_INFO_TEXT = (
    "Как тебе эта информация? Была ли она полезной?\n\n"
    "Если хочешь глубже разобраться в своей нумерологической карте, подписывайся на мой тг-канал."
)

KEY_IMAGE_URL = "https://i.pinimg.com/736x/a0/a9/70/a0a970e2ab1807b52dd46b3261549509.jpg"

START_KEYBOARD = ReplyKeyboardMarkup(
    [[KeyboardButton("🚀 Запустить бота")]],
    resize_keyboard=True,
    one_time_keyboard=True
)

# ======= Клавиатуры =========
def get_subscription_markup():
    keyboard = [
        [InlineKeyboardButton("📢 Подписаться на канал", url=CHANNEL_LINK)],
        [
            InlineKeyboardButton("▶️ Продолжить", callback_data="continue"),
            InlineKeyboardButton("🚪 Уйти", callback_data="exit")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_main_menu_markup(user_id=None):
    is_admin = user_id == ADMIN_ID
    keyboard = [
        [InlineKeyboardButton("ℹ️ Помощь", callback_data="help")],
        [InlineKeyboardButton("📅 Рассчет по дню рождения", callback_data="birthday_calc")],
        [InlineKeyboardButton("🚪 Уйти", callback_data="exit")]
    ]
    if is_admin:
        keyboard.append([InlineKeyboardButton("📝 Новый пост", callback_data="new_post")])
    return InlineKeyboardMarkup(keyboard)

def get_next_key_markup():
    return InlineKeyboardMarkup([[InlineKeyboardButton("➡️ Далее", callback_data="next_key")]])

def get_final_menu_markup():
    keyboard = [
        [InlineKeyboardButton("🏠 Меню", callback_data="menu")],
        [InlineKeyboardButton("🚪 Уйти", callback_data="exit")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_preview_markup():
    keyboard = [
        [InlineKeyboardButton("✅ Отправить всем", callback_data="broadcast_post"),
         InlineKeyboardButton("❌ Отменить", callback_data="cancel_post")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ======= Работа с JSON =========
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_user(user_id):
    users = load_users()
    if user_id not in users:
        users.append(user_id)
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False)

# ======= Проверка подписки ===========

async def check_subscription(user_id, context: ContextTypes.DEFAULT_TYPE):
    try:
        member = await context.bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logger.warning(f"Ошибка проверки подписки: {e}")
        return False

# ======= Старт =========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user(user.id)
    await update.message.reply_text(
        f"👋 Привет, {user.first_name}! Бот готов к работе. Выберите действие ниже.",
        reply_markup=START_KEYBOARD
    )

# ======= Подписка =======
async def send_subscription_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "❌ <b>Вы не подписаны на канал.</b>\n"
        "Пожалуйста, подпишитесь, чтобы пользоваться ботом.\n"
        "Нажмите 'Продолжить' после подписки для проверки."
    )
    if update.message:
        await update.message.reply_html(text, reply_markup=get_subscription_markup())
    elif update.callback_query:
        try:
            await update.callback_query.edit_message_text(text, reply_markup=get_subscription_markup(), parse_mode="HTML")
        except:
            pass

# ======= Главное меню =======
async def send_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = f"👋 Привет, {user.first_name}! Бот готов к работе. Выберите действие ниже."
    if update.message:
        await update.message.reply_text(text, reply_markup=get_main_menu_markup(user.id))
    elif update.callback_query:
        try:
            await update.callback_query.edit_message_text(text, reply_markup=get_main_menu_markup(user.id))
        except:
            await update.callback_query.message.delete()
            await update.callback_query.message.chat.send_message(text, reply_markup=get_main_menu_markup(user.id))

# ======= Доп. информация =======
async def send_additional_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("📢 Подписаться на канал", url=CHANNEL_LINK)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.effective_chat.send_message(ADDITIONAL_INFO_TEXT, reply_markup=reply_markup)

# ======= Продолжить после подписки =======
async def continue_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    if await check_subscription(user.id, context):
        await send_main_menu(update, context)
    else:
        await send_subscription_panel(update, context)

# ======= Кнопка "Уйти" =======
async def exit_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await send_additional_info(update, context)
    try:
        await query.message.delete()
    except:
        pass

# ======= Логика главного меню =======
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    if data == "help":
        await query.edit_message_text("ℹ️ Здесь будет помощь по боту. Введите /help для справки.")
    elif data == "birthday_calc":
        intro_text = (
            "Ты знаешь, что твоя дата рождения — это не просто цифры в паспорте?\n\n"
            "Это личный код Вселенной, в котором зашифрованы:\n"
            "✔ Твои врождённые таланты — что у тебя получается легко, а что нужно развивать.\n"
            "✔ Финансовые энергии — почему одни люди притягивают деньги, а другим они «утекают».\n"
            "✔ Канал вдохновения — откуда к тебе приходят гениальные идеи и как не потерять связь со своим предназначением.\n\n"
            "Сейчас я помогу тебе раскрыть **3 главных ключа** из твоей даты рождения:\n\n"
            "📅 Введи свою дату рождения в формате ДД.ММ.ГГГГ\n"
            "Например: *26.08.1996*"
        )
        await query.edit_message_text(intro_text, parse_mode="Markdown")
        return ASK_BIRTHDATE
    elif data == "menu":
        await send_main_menu(update, context)
    elif data == "exit":
        await exit_callback(update, context)
    elif data == "new_post" and user_id == ADMIN_ID:
        await query.message.reply_text("Введите текст нового поста:")
        return NEW_POST_TEXT

# ======= Расчёт ключей =======
def reduce_to_limit(number: int, limit: int) -> int:
    while number > limit:
        number = sum(int(d) for d in str(number))
    return number

def reduce_to_single_digit(number: int) -> int:
    while number > 9:
        number = sum(int(d) for d in str(number))
    return number

def calculate_energies(day: int, month: int, year: int):
    consciousness = reduce_to_limit(day, 22)
    material = reduce_to_single_digit(year)
    soul = month
    return consciousness, material, soul

# ======= Отправка ключа с картинкой =======
async def send_key_with_image(chat, key_title, key_number, key_text):
    try:
        await chat.send_photo(
            photo=KEY_IMAGE_URL,
            caption=f"{key_title} ({key_number}):\n{key_text}",
            reply_markup=get_next_key_markup()
        )
    except:
        await chat.send_message(f"{key_title} ({key_number}):\n{key_text}", reply_markup=get_next_key_markup())

# ======= Получение даты рождения =======
async def birthday_calc_receive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    try:
        birthdate = datetime.datetime.strptime(text, "%d.%m.%Y")
    except ValueError:
        await update.message.reply_text("Неверный формат даты. Используйте ДД.MM.ГГГГ.")
        return ASK_BIRTHDATE

    day, month, year = birthdate.day, birthdate.month, birthdate.year
    consciousness, material, soul = calculate_energies(day, month, year)

    context.user_data['keys'] = [
        ("🔢 Энергия сознания", consciousness, CONSCIOUSNESS_ENERGY_TEXTS[consciousness]),
        ("🏋️‍♂️ Энергия материи", material, MATERIAL_ENERGY_TEXTS[material]),
        ("🕊️ Энергия души", soul, SOUL_ENERGY_TEXTS[soul])
    ]
    context.user_data['current_key_index'] = 0

    key_title, key_number, key_text = context.user_data['keys'][0]
    await send_key_with_image(update.message.chat, key_title, key_number, key_text)
    return SHOWING_KEYS

# ======= Пошаговое отображение ключей =======
async def next_key_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    idx = context.user_data.get('current_key_index', 0) + 1
    keys = context.user_data.get('keys', [])

    try:
        await query.edit_message_reply_markup(reply_markup=None)
    except:
        pass

    if idx < len(keys):
        key_title, key_number, key_text = keys[idx]
        context.user_data['current_key_index'] = idx
        await send_key_with_image(query.message.chat, key_title, key_number, key_text)
        return SHOWING_KEYS
    else:
        await query.message.chat.send_message(
            "✅ Это все ключи из твоей даты рождения.",
            reply_markup=get_final_menu_markup()
        )
        return ConversationHandler.END

# ======= Новый пост (админ) =======
async def new_post_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['post_text'] = update.message.text
    await update.message.reply_text("Теперь отправьте картинку для поста (или /skip если без картинки).")
    return NEW_POST_IMAGE

async def new_post_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo
    if photo:
        file_id = photo[-1].file_id
        context.user_data['post_image'] = file_id
    await preview_post(update, context)
    return PREVIEW_POST

async def skip_post_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['post_image'] = None
    await preview_post(update, context)
    return PREVIEW_POST

async def preview_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = context.user_data.get('post_text')
    image = context.user_data.get('post_image')
    if image:
        await update.message.reply_photo(photo=image, caption=text, reply_markup=get_preview_markup())
    else:
        await update.message.reply_text(text, reply_markup=get_preview_markup())

async def preview_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == "broadcast_post":
        await broadcast_post(query, context)
        return ConversationHandler.END
    elif data == "cancel_post":
        await query.message.reply_text("❌ Рассылка отменена.")
        return ConversationHandler.END

async def broadcast_post(update_or_query, context: ContextTypes.DEFAULT_TYPE):
    text = context.user_data.get('post_text')
    image = context.user_data.get('post_image')
    users = load_users()

    for user_id in users:
        try:
            if image:
                await context.bot.send_photo(chat_id=user_id, photo=image, caption=text)
            else:
                await context.bot.send_message(chat_id=user_id, text=text)
        except Exception as e:
            logger.warning(f"Не удалось отправить пользователю {user_id}: {e}")

    if isinstance(update_or_query, Update):
        await update_or_query.message.reply_text("✅ Пост успешно разослан всем пользователям!")
    else:
        await update_or_query.message.reply_text("✅ Пост успешно разослан всем пользователям!")

# ======= /help =======
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "ℹ️ <b>Помощь по боту:</b>\n"
        "/start — начать работу с ботом\n"
        "/help — показать это сообщение\n\n"
        "Для использования бота необходимо быть подписанным на канал.\n"
        f"Подписка: {CHANNEL_LINK}"
    )
    await update.message.reply_html(text)

# ======= /cancel =======
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Операция отменена.")
    return ConversationHandler.END

# ======= Обработка любых других сообщений =======
async def default_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🚀 Запустить бота":
        user = update.effective_user
        if await check_subscription(user.id, context):
            await send_main_menu(update, context)
        else:
            await send_subscription_panel(update, context)
    else:
        await update.message.reply_text(
            "Привет! Чтобы начать работу с ботом, пожалуйста, нажмите кнопку '🚀 Запустить бота'.",
            reply_markup=START_KEYBOARD
        )

# ======= MAIN =========
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # ===== Conversation для ключей =====
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler, pattern="^birthday_calc$")],
        states={
            ASK_BIRTHDATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, birthday_calc_receive)],
            SHOWING_KEYS: [CallbackQueryHandler(next_key_handler, pattern="^next_key$")]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True
    )

    # ===== Conversation для поста (админ) =====
    admin_post_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler, pattern="^new_post$")],
        states={
            NEW_POST_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, new_post_text)],
            NEW_POST_IMAGE: [
                MessageHandler(filters.PHOTO, new_post_image),
                CommandHandler("skip", skip_post_image)
            ],
            PREVIEW_POST: [CallbackQueryHandler(preview_button_handler, pattern="^(broadcast_post|cancel_post)$")]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(continue_callback, pattern="^continue$"))
    app.add_handler(CallbackQueryHandler(exit_callback, pattern="^exit$"))
    app.add_handler(conv_handler)
    app.add_handler(admin_post_conv)
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, default_handler))

    logger.info("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
