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
    "Если хочешь глубже разобраться в своей нумерологической карте, подписывайся на мой тг-канал «Сонастройка с Ульяной. Там я делюсь разборами, лайфхаками по нумерологии и толкованием снов. »"
)
# ======= Картинки для чисел каждого ключа =======
KEY_IMAGES = {
    "consciousness": {
        1: "https://drive.google.com/uc?export=download&id=1d9RP3chTKoUhuxXKGHbHPaXtIh41fQdd",
        2: "https://drive.google.com/uc?export=download&id=15Ql5OgpxOtJ5vc-_lDEI1WcPW69u0koX",
        3: "https://drive.google.com/uc?export=download&id=1Xugd4Lj6rmN7b3TqMU8Kea3pBeDgH0d6",
        4: "https://drive.google.com/uc?export=download&id=1ZPSgYUUMJJn8SaC8v2PLdq3YKqsfO5u0",
        5: "https://drive.google.com/uc?export=download&id=17h-nZi8Jr1-bbBt_qOsaBGY11X56jQIZ",
        6: "https://drive.google.com/uc?export=download&id=1DV9VO3q0njY6NJcX7sNmMjgDQSDSiuB_",
        7: "https://drive.google.com/uc?export=download&id=1C8VKXqvnnOnt_-J-lHwpXIeNC5-YAQ3o",
        8: "https://drive.google.com/uc?export=download&id=1_SFu00EItAsIXSJ2bAd2fr_fy0FR2FmE",
        9: "https://drive.google.com/uc?export=download&id=15QWjstMC5n9j93rBbtA1iTHIpB6zIAtr",
        10: "https://drive.google.com/uc?export=download&id=16DMDf5qyXPzgoU4WWWk9cBCehOJ9RYzm",
        11: "https://drive.google.com/uc?export=download&id=1x7xMuvA7UorpNNfOsLBacihfZGKTuGou",
        12: "https://drive.google.com/uc?export=download&id=1E6bOylGqrcA142h7eXgGHiSnwD6tXLY7",
        13: "https://drive.google.com/uc?export=download&id=182vQNBam-NQiH-txNgcchqOcPm4ux_Do",
        14: "https://drive.google.com/uc?export=download&id=1a3BbKrUxOSg084UIu299gvxehzBKilFk",
        15: "https://drive.google.com/uc?export=download&id=1GFoTP0PxQHgWpLImb8u_mPo60bOfx-oK",
        16: "https://drive.google.com/uc?export=download&id=1YILJ1YRY4HM3v0loVAqsy2f6OaEOgOSc",
        17: "https://drive.google.com/uc?export=download&id=1DJi93iQs4UQFRoITnTOuSh6Qo_zURDtT",
        18: "https://drive.google.com/uc?export=download&id=1FMttXsBJctwbKjz_DV_z-Loc7sqwyWRp",
        19: "https://drive.google.com/uc?export=download&id=14JyzC-Ha4BeYamZyAjxNbeu4t0u5gboO",
        20: "https://drive.google.com/uc?export=download&id=1BIgYMRNbHkvojCFyZAEIEQdJQf9-Su3S",
        21: "https://drive.google.com/uc?export=download&id=1RmCVWQzgegL4UL_tARkKH1pfBXeKv4hw",
        22: "https://drive.google.com/uc?export=download&id=1_hWt3VDHPo5p7yZrBdyY5hPTWB6EvUDA"
    },
    "material": {
        1: "https://drive.google.com/uc?export=download&id=1b6Id_PKwKy-XoZ3Lwuf5694NmPnhrlsx",
        2: "https://drive.google.com/uc?export=download&id=12W57_-QP-OI0f6HOR7JB1FwOndI_tn6a",
        3: "https://drive.google.com/uc?export=download&id=1YDyQ5dSTg_jqq5YfqZGoApWaNDUmUkTe",
        4: "https://drive.google.com/uc?export=download&id=17PmcBBrdo1SHlgJH7buOYhdr97F1QalL",
        5: "https://drive.google.com/uc?export=download&id=1njO8jjFhxi0Hgy3Nkvb5pC01_E55BETR",
        6: "https://drive.google.com/uc?export=download&id=1HBiBLkmq-7bobT98sTs3GffcJTKwSNdF",
        7: "https://drive.google.com/uc?export=download&id=1WeoVha3JaoOAy4eLLeEyztf_hiYx_oZE",
        8: "https://drive.google.com/uc?export=download&id=1EQ0I0SE0b7QiDtlUPO8bDN3BR9yt8PRw",
        9: "https://drive.google.com/uc?export=download&id=1oCLlpzYWLy2TqiIUbs-aExf0U-no-vEj"
    },
    "soul": {
        1: "https://drive.google.com/uc?export=download&id=1i5SQRB1OHNi9pTCQ4vagnb-BOs1ZwXml",
        2: "https://drive.google.com/uc?export=download&id=1vKKUufczbnSB8-UWGvAGxDrCXGPMKUjK",
        3: "https://drive.google.com/uc?export=download&id=1vVyZf17S70CpGEcA7fTAtb9G_ALuLfg3",
        4: "https://drive.google.com/uc?export=download&id=1bmzmzEV7P4vu79PRQHzBB8Xy0TKxp0nZ",
        5: "https://drive.google.com/uc?export=download&id=15kIq4gnkV4V2wrLnOHl1wyaBpFwmj_ZS",
        6: "https://drive.google.com/uc?export=download&id=114weFwXxJvBG5s-sTdbpo0mzXgGH84d6",
        7: "https://drive.google.com/uc?export=download&id=1d2KIja0TCVur_8nAe6GANb4movVP1Jyy",
        8: "https://drive.google.com/uc?export=download&id=1IZZTPD_DVdHL2gsH2NkR3EKRGraGULAE",
        9: "https://drive.google.com/uc?export=download&id=1VdSPPy3yLKbDXI8fYs2hGCeyEfNtcF0L",
        10: "https://drive.google.com/uc?export=download&id=1lbsedB_uUoBWZR0P47bUyCgUAiMNoZ6L",
        11: "https://drive.google.com/uc?export=download&id=15JTj5UXphUyEe5A4IxALdNhHIeJbuWre",
        12: "https://drive.google.com/uc?export=download&id=1NLk5-8Zrcm21htO0d6lGLnSOWSVwmc81"
    }
}
# ======= Состояния =======
ASK_BIRTHDATE = 0
SHOWING_KEYS = 1
NEW_POST_TEXT = 2
NEW_POST_IMAGE = 3
PREVIEW_POST = 4
CONFIRM_BIRTHDATE = 5

# ======= Клавиатуры =======
START_KEYBOARD = ReplyKeyboardMarkup(
    [[KeyboardButton("⚡️ Запустить помощника")]],
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
        [InlineKeyboardButton("📅 Рассчет по дню рождения", callback_data="birthday_calc")],
        [InlineKeyboardButton("ℹ️ Помощь", callback_data="help")],
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
        f"👋 Привет, {user.first_name}! Запусти помощника.",
        reply_markup=START_KEYBOARD
    )

# ======= Подписка =======
async def send_subscription_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "❌ <b>Вы не подписаны на канал.</b>\n"
        "Пожалуйста, подпишитесь, чтобы пользоваться помощником.\n"
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
    text = f"Помощник готов к работе. Выберите действие ниже."
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
        await query.edit_message_text("ℹ️ Здесь будет помощь по помощнику. Введите /help для справки.")
    elif data == "birthday_calc":
        intro_text = (
            "Ты знаешь, что твоя дата рождения — это не просто цифры в паспорте?\n\n"
            "Это личный код Вселенной, в котором зашифрованы:\n"
            "✔ Твои врождённые таланты — что у тебя получается легко, а что нужно развивать.\n"
            "✔ Финансовые энергии — почему одни люди притягивают деньги, а другим они «утекают».\n"
            "✔ Канал вдохновения — откуда к тебе приходят гениальные идеи и как не потерять связь со своим предназначением.\n\n"
            "Сейчас я помогу тебе раскрыть 3 главных ключа из твоей даты рождения:\n\n"
            "📅 Введи свою дату рождения в формате ДД.ММ.ГГГГ\n"
            "Например: 26.08.1996"
        )
        await query.edit_message_text(intro_text, parse_mode="Markdown")
        return ASK_BIRTHDATE
    elif data == "menu":
        await send_main_menu(update, context)
    elif data == "exit":
        await exit_callback(update, context)
    elif data == "new_post" and user_id == ADMIN_ID:
        await query.message.reply_text("Введите текст нового поста:")
    elif data == "restart_birthday":
        await query.edit_message_text(
            "📅 Введи свою дату рождения в формате ДД.ММ.ГГГГ\nНапример: 26.08.1996"
        )
        return ASK_BIRTHDATE
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

# ======= Ввод даты рождения =======
async def birthday_calc_receive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    try:
        birthdate = datetime.datetime.strptime(text, "%d.%m.%Y")
    except ValueError:
        await update.message.reply_text("❌ Неверный формат даты. Используйте ДД.MM.ГГГГ.")
        return ASK_BIRTHDATE
    keyboard = [
        [InlineKeyboardButton("✅ Да", callback_data="confirm_date")],
        [InlineKeyboardButton("⛔ Нет", callback_data="reject_date")]
    ]

    # сохраняем дату в user_data
    context.user_data["birthdate"] = birthdate

    # предлагаем подтвердить
    keyboard = [
        [InlineKeyboardButton("✅ Да", callback_data="confirm_date")],
        [InlineKeyboardButton("⛔ Нет", callback_data="reject_date")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"Твоя дата рождения — {birthdate.strftime('%d.%m.%Y')}\nВсе верно? 🤍",
        reply_markup=reply_markup
    )
    return CONFIRM_BIRTHDATE


# ======= Подтверждение даты =======
async def confirm_birthdate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "confirm_date":
        birthdate = context.user_data["birthdate"]
        day, month, year = birthdate.day, birthdate.month, birthdate.year

        # рассчитываем энергии
        consciousness, material, soul = calculate_energies(day, month, year)

        # сохраняем ключи
        context.user_data['keys'] = [
            {"type": "consciousness", "title": " Энергия сознания", "number": consciousness,
             "text": CONSCIOUSNESS_ENERGY_TEXTS.get(str(consciousness)) or "Описание пока не добавлено"},
            {"type": "material", "title": "🏋️♂️ Энергия материи", "number": material,
             "text": MATERIAL_ENERGY_TEXTS.get(str(material)) or "Описание пока не добавлено"},
            {"type": "soul", "title": " Энергия души", "number": soul,
             "text": SOUL_ENERGY_TEXTS.get(str(soul)) or "Описание пока не добавлено"}
        ]
        context.user_data['current_key_index'] = 0

        # отправляем первый ключ
        first_key = context.user_data['keys'][0]
        image_url = KEY_IMAGES[first_key['type']].get(first_key['number'])
        await send_key_with_image(
            query.message.chat,
            first_key['title'],
            first_key['number'],
            first_key['text'],
            image_url=image_url
        )
        return SHOWING_KEYS

    elif query.data == "reject_date":
        await query.edit_message_text(
            "Ничего страшного, со всеми бывает!\n\n"
            "Давай попробуем ещё раз 👇\n\n"
            "Введи верную дату в формате ДД.ММ.ГГГГ\n"
            "Например: 03.06.1995"
        )
        return ASK_BIRTHDATE


# ======= Показ следующего ключа =======
async def next_key_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Убираем кнопку "➡️ Далее" после нажатия
    try:
        await query.edit_message_reply_markup(reply_markup=None)
    except Exception as e:
        logger.warning(f"Не удалось убрать кнопки: {e}")

    # увеличиваем индекс
    context.user_data['current_key_index'] += 1
    index = context.user_data['current_key_index']

    # если ключи ещё есть → показываем следующий
    if index < len(context.user_data['keys']):
        key = context.user_data['keys'][index]
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
        # если ключи закончились, показываем сообщение + кнопки
        keyboard = [
            [InlineKeyboardButton("📅 Ввести дату рождения ещё раз", callback_data="restart_birthday")],
            [InlineKeyboardButton("🏠 Меню", callback_data="menu")],
            [InlineKeyboardButton("📝 Запись на консультацию", url="https://t.me/num_insight/8")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.message.reply_text(
            "Как тебе эта информация? Была ли она полезной?\n\n"
            "Если хочешь глубже разобраться в своей нумерологической карте, переходи в мой тг-канал «Сонастройка с Ульяной»\n\n"
            "Там я делюсь разборами, лайфхаками по нумерологии и толкованием снов.\n\n"
            "А если чувствуешь, что хочешь полную расшифровку своей даты рождения, чтобы понять:\n\n"
            "💰 Почему деньги приходят с трудом?\n"
            "🌟 В чём твоя истинная реализация?\n"
            "💡 Какие таланты стоит развивать?\nМожешь записаться ко мне на личную консультацию. Буду рада помочь ✨",

            reply_markup=reply_markup
        )
        return SHOWING_KEYS  # остаёмся в том же состоянии, чтобы можно было вводить дату снова

# ======= Функция отправки ключа с картинкой =======
async def send_key_with_image(chat, key_title, key_number, key_text, image_url=None):
    placeholder = None
    if image_url:
        try:
            # Отправляем сообщение-заглушку
            placeholder = await chat.send_message("⏳ Рассчитываем энергию...")

            await chat.send_photo(photo=image_url)  # без caption
        except Exception as e:
            await chat.send_message(f"⚠️ Не удалось отправить картинку: {e}")
        finally:
            if placeholder:
                try:
                    await placeholder.delete()
                except:
                    pass

    await chat.send_message(
        key_text,
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
        "ℹ️ <b>Помощь по помощнику:</b>\n"
        "/start — начать работу с помощником\n"
        "/help — показать это сообщение\n\n"
        "Для использования помощника необходимо быть подписанным на канал.\n"
        f"Подписка: {CHANNEL_LINK}"
    )
    await update.message.reply_html(text)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Операция отменена.")
    return ConversationHandler.END

# ======= Обработка любых сообщений =======
async def default_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return  # игнорируем всё, что не является текстом

    text = update.message.text.strip()
    if text == "⚡️ Запустить помощника":
        user = update.effective_user
        if await check_subscription(user.id, context):
            await send_main_menu(update, context)
        else:
            await send_subscription_panel(update, context)
    else:
        await update.message.reply_text(
            "Привет! Чтобы начать работу с помощником, пожалуйста, нажмите кнопку '⚡️ Запустить помощника'.",
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
            CONFIRM_BIRTHDATE: [CallbackQueryHandler(confirm_birthdate, pattern="^(confirm_date|reject_date)$")],
            SHOWING_KEYS: [CallbackQueryHandler(next_key_handler, pattern="^next_key$"),
                           CallbackQueryHandler(button_handler, pattern="^(menu|exit|restart_birthday)$")
            ]
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
