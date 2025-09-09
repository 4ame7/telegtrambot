from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, KeyboardButton
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, ContextTypes, filters
)
import logging
import datetime
import json
import os

# ======= Настройки =======
BOT_TOKEN = "7739338057:AAHFzDpOgh-XrBr-vqWvV5TEqKs62HQS9zY"
CHANNEL_ID = -1002496521038
CHANNEL_LINK = "https://t.me/num_insight"
ADMIN_ID = 405069873
USERS_FILE = "users.json"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ======= Загрузка энергий из JSON =======
with open("energies.json", "r", encoding="utf-8") as f:
    ENERGIES = json.load(f)

CONSCIOUSNESS_ENERGY_TEXTS = ENERGIES.get("consciousness", {})
MATERIAL_ENERGY_TEXTS = ENERGIES.get("material", {})
SOUL_ENERGY_TEXTS = ENERGIES.get("soul", {})

# ======= Тексты =======
ADDITIONAL_INFO_TEXT = (
    "Как тебе эта информация? Была ли она полезной?\n\n"
    "Если хочешь глубже разобраться в своей нумерологической карте, подписывайся на мой тг-канал."
)
# ======= Картинки для чисел каждого ключа =======
KEY_IMAGES = {
    "consciousness": {
        1: "https://static.tildacdn.com/tild3432-6364-4231-b537-626438323165/star_start.jpg",
        2: "https://i.pinimg.com/736x/02.jpg",
        3: "https://i.pinimg.com/736x/03.jpg",
        4: "https://i.pinimg.com/736x/04.jpg",
        5: "https://i.pinimg.com/736x/05.jpg",
        6: "https://i.pinimg.com/736x/06.jpg",
        7: "https://i.pinimg.com/736x/07.jpg",
        8: "https://i.pinimg.com/736x/08.jpg",
        9: "https://i.pinimg.com/736x/09.jpg",
        10: "https://i.pinimg.com/736x/10.jpg",
        11: "https://i.pinimg.com/736x/11.jpg",
        12: "https://i.pinimg.com/736x/12.jpg",
        13: "https://i.pinimg.com/736x/13.jpg",
        14: "https://i.pinimg.com/736x/14.jpg",
        15: "https://i.pinimg.com/736x/15.jpg",
        16: "https://i.pinimg.com/736x/16.jpg",
        17: "https://i.pinimg.com/736x/17.jpg",
        18: "https://i.pinimg.com/736x/18.jpg",
        19: "https://i.pinimg.com/736x/19.jpg",
        20: "https://i.pinimg.com/736x/20.jpg",
        21: "https://i.pinimg.com/736x/21.jpg",
        22: "https://i.pinimg.com/736x/22.jpg"
    },
    "material": {
        1: "https://i.pinimg.com/736x/m1.jpg",
        2: "https://i.pinimg.com/736x/m2.jpg",
        3: "https://i.pinimg.com/736x/m3.jpg",
        4: "https://i.pinimg.com/736x/m4.jpg",
        5: "https://i.pinimg.com/736x/m5.jpg",
        6: "https://i.pinimg.com/736x/m6.jpg",
        7: "https://i.pinimg.com/736x/m7.jpg",
        8: "https://i.pinimg.com/736x/m8.jpg",
        9: "https://i.pinimg.com/736x/m9.jpg"
    },
    "soul": {
        1: "https://i.pinimg.com/736x/s1.jpg",
        2: "https://i.pinimg.com/736x/s2.jpg",
        3: "https://i.pinimg.com/736x/s3.jpg",
        4: "https://i.pinimg.com/736x/s4.jpg",
        5: "https://i.pinimg.com/736x/s5.jpg",
        6: "https://i.pinimg.com/736x/s6.jpg",
        7: "https://i.pinimg.com/736x/s7.jpg",
        8: "https://i.pinimg.com/736x/s8.jpg",
        9: "https://i.pinimg.com/736x/s9.jpg",
        10: "https://i.pinimg.com/736x/s10.jpg",
        11: "https://i.pinimg.com/736x/s11.jpg",
        12: "https://i.pinimg.com/736x/s12.jpg"
    }
}
# ======= Состояния =======
ASK_BIRTHDATE = 0
SHOWING_KEYS = 1
NEW_POST_TEXT = 2
NEW_POST_IMAGE = 3
PREVIEW_POST = 4

# ======= Клавиатуры =======
START_KEYBOARD = ReplyKeyboardMarkup(
    [[KeyboardButton("🚀 Запустить бота")]],
    resize_keyboard=True,
    one_time_keyboard=True
)

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

# ======= Работа с пользователями =======
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

# ======= Проверка подписки =======
async def check_subscription(user_id, context: ContextTypes.DEFAULT_TYPE):
    try:
        member = await context.bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logger.warning(f"Ошибка проверки подписки: {e}")
        return False

# ======= Бот: старт =======
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

# ======= Кнопки "Продолжить" и "Уйти" =======
async def continue_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    if await check_subscription(user.id, context):
        await send_main_menu(update, context)
    else:
        await send_subscription_panel(update, context)

async def exit_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await send_additional_info(update, context)
    try:
        await query.message.delete()
    except:
        pass

# ======= Главная логика меню =======
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

# ======= Функции для расчёта =======
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

    # Сохраняем ключи в user_data с типом для картинки
    context.user_data['keys'] = [
        {"type": "consciousness", "title": "🔢 Энергия сознания", "number": consciousness,
         "text": CONSCIOUSNESS_ENERGY_TEXTS.get(str(consciousness)) or "Описание пока не добавлено"},
        {"type": "material", "title": "🏋️‍♂️ Энергия материи", "number": material,
         "text": MATERIAL_ENERGY_TEXTS.get(str(material)) or "Описание пока не добавлено"},
        {"type": "soul", "title": "🕊️ Энергия души", "number": soul,
         "text": SOUL_ENERGY_TEXTS.get(str(soul)) or "Описание пока не добавлено"}
    ]
    context.user_data['current_key_index'] = 0

    # Отправляем первый ключ с картинкой по числу
    first_key = context.user_data['keys'][0]
    image_url = KEY_IMAGES[first_key['type']].get(first_key['number'])
    await send_key_with_image(
        update.message.chat,
        first_key['title'],
        first_key['number'],
        first_key['text'],
        image_url=image_url
    )
    return SHOWING_KEYS


# ======= Пошаговое отображение ключей =======
async def next_key_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    idx = context.user_data.get('current_key_index', 0) + 1
    keys = context.user_data.get('keys', [])

    # Убираем старую кнопку "Далее"
    try:
        await query.edit_message_reply_markup(reply_markup=None)
    except:
        pass

    if idx < len(keys):
        key = keys[idx]
        context.user_data['current_key_index'] = idx
        image_url = KEY_IMAGES[key['type']].get(key['number'])
        await send_key_with_image(
            query.message.chat,
            key['title'],
            key['number'],
            key['text'],
            image_url=image_url
        )
        return SHOWING_KEYS
    else:
        # Конец всех ключей — показываем финальное меню
        await query.message.chat.send_message(
            "✅ Это все ключи из твоей даты рождения.",
            reply_markup=get_final_menu_markup()
        )
        return ConversationHandler.END


# ======= Функция отправки ключа с картинкой =======
async def send_key_with_image(chat, key_title, key_number, key_text, image_url=None):
    if image_url:
        try:
            await chat.send_photo(photo=image_url)  # без caption
        except Exception as e:
            await chat.send_message(f"⚠️ Не удалось отправить картинку: {e}")

    # Текст всегда отправляем отдельным сообщением
    await chat.send_message(
        f"{key_title} ({key_number}):\n{key_text}",
        reply_markup=get_next_key_markup()
    )

# ======= Админ: новый пост =======
async def new_post_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['post_text'] = update.message.text
    await update.message.reply_text("Теперь отправьте картинку для поста (или /skip если без картинки).")
    return NEW_POST_IMAGE

async def new_post_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo
    if photo:
        context.user_data['post_image'] = photo[-1].file_id
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

    await update_or_query.message.reply_text("✅ Пост успешно разослан всем пользователям!")

# ======= /help и /cancel =======
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "ℹ️ <b>Помощь по боту:</b>\n"
        "/start — начать работу с ботом\n"
        "/help — показать это сообщение\n\n"
        "Для использования бота необходимо быть подписанным на канал.\n"
        f"Подписка: {CHANNEL_LINK}"
    )
    await update.message.reply_html(text)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Операция отменена.")
    return ConversationHandler.END

# ======= Обработка любых сообщений =======
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

# ======= MAIN =======
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # ConversationHandler для ключей
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler, pattern="^birthday_calc$")],
        states={
            ASK_BIRTHDATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, birthday_calc_receive)],
            SHOWING_KEYS: [CallbackQueryHandler(next_key_handler, pattern="^next_key$")]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True
    )

    # ConversationHandler для админского поста
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
    app.add_handler(CallbackQueryHandler(button_handler, pattern="^(help|birthday_calc|menu|exit|new_post)$"))

    logger.info("Бот запущен...")
    app.run_polling()


if __name__ == "__main__":
    main()
