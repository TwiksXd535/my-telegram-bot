import asyncio
import logging
import random
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import os
import threading
from flask import Flask
import requests
import tempfile

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# ВСТАВЬ СВОЙ ТОКЕН
BOT_TOKEN = "8771879640:AAFZBm7PsWXCOMYTNkL0LLz0qfup0nW8_z4"
ADMIN_ID = 5598887326

# Создаем объекты бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# === ХРАНИЛИЩЕ ДАННЫХ ===
users_db = {}

# === РУССКИЕ ШУТКИ (твои) ===
JOKES = [
    "Идет Штирлиц по улице и видит лужу, и думает — похуй, а оказалось — по нос 👃",
    "Милиция стала Полицией, а Медики все еще ждут своей очереди 🚑",
    "Как бы черный сушист не пытался скрутить роллы, всё равно получается косяк 🍣",
    "Знаете, чем пожертвовал создатель первой посудомойки?\nРебром 🍽️",
    "Едет мужик в автобусе домой и резко орет:\n— Ахуеть, да ну нахуй!\nНа него все укоризненно смотрят: вы же в общественном месте!\nА он говорит:\n— У меня тройня родилась!\nТолпа:\n— Ахуеть!\nМужик:\n— И все три негры!\nТолпа:\n— ДА НУ НАХУЙ! 🚌",
    "Стэндоф 9, а отчимов 2 — как мне добавить эти анекдоты? 😂",
    "— Доктор, у меня проблема: я всё время говорю сам с собой.\n— Это не проблема, многие так делают.\n— Да, но я такой скучный собеседник!",
    "Встречаются два программиста:\n— Ты знаешь, я вчера купил себе умный будильник.\n— И как?\n— Он такой умный, что научился звонить на работу и говорить, что я заболел.",
    "Пришел мужик к врачу и говорит: так мол и так, живот болит уже 2 дня.\nВрач посмотрел на него и говорит:\n— Так ты ж беременный!\nУ мужика глаза на лоб полезли:\n— Как беременный?!\nА врач ему:\n— Ну вот такая аномалия, держи эти таблетки и пей по одной в день.\n\nУходит мужик поникший и вдруг как заболел у него живот, скрутило так, что он решил все таблетки разом выпить.\nА уже через 10 минут приспичило ему мама не горюй.\nНашел он люк ближайший, спустил штаны и выпустил все из себя.\nТолько почувствовал мужик облегчение, как из канализации доносится:\n— Ой, мама...\n\nУ мужика глаза опять на лоб полезли, подскочил он и начал ногами запихивать рабочего обратно и кричать:\n— Сирота ты, сирота!!! 👶🚽",
]

# === РУССКИЕ ЦИТАТЫ ===
QUOTES = [
    "Жизнь — это то, что с тобой происходит, пока ты строишь планы. — Джон Леннон",
    "Будь тем изменением, которое хочешь увидеть в мире. — Махатма Ганди",
    "Сложнее всего начать действовать, все остальное зависит только от упорства. — Амелия Эрхарт",
    "Глаза боятся, а руки делают. — русская пословица",
    "Тише едешь — дальше будешь. — русская пословица",
]

# === ТЕКСТОВЫЕ МЕМЫ (запасной вариант) ===
TEXT_MEMES = [
    "😂 Мем дня:\n\nКогда проснулся, а уже понедельник",
    "😂 Мем:\n\n*Заходит в магазин*\n— Мне чек, пожалуйста\n— Оплата картой?\n— Нет, просто чек, я коллекционирую",
    "😂 Мем:\n\n— Ты где работаешь?\n— В IT\n— А кем?\n— Ну... сижу в интернете целый день\n— Так ты безработный?\n— Нет, я тестировщик",
]

# === ФАКТЫ ===
FACTS = [
    "🔍 В России есть город с названием «Мышкин».",
    "🔍 Байкал — самое глубокое озеро в мире.",
    "🔍 Московский Кремль — самая большая средневековая крепость в Европе.",
]

# === ФУНКЦИЯ ДЛЯ ПОЛУЧЕНИЯ МЕМА-КАРТИНКИ ===
def get_meme_image():
    """Получает случайный мем-картинку из интернета"""
    try:
        response = requests.get("https://meme-api.com/gimme", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('url')
        else:
            return None
    except:
        return None

# === СОЗДАНИЕ МЕНЮ ===
def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🤣 Шутка"), KeyboardButton(text="📜 Цитата")],
            [KeyboardButton(text="😂 Мем"), KeyboardButton(text="🔍 Факт")],
            [KeyboardButton(text="👤 Мой профиль")]
        ],
        resize_keyboard=True
    )
    return keyboard

# === СОХРАНЕНИЕ ПОЛЬЗОВАТЕЛЯ ===
async def save_user(message: types.Message):
    user = message.from_user
    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    
    if user.id not in users_db:
        users_db[user.id] = {
            "name": user.first_name,
            "username": user.username,
            "first_seen": now,
            "messages": 1
        }
        if user.id != ADMIN_ID:
            print(f"🆕 Новый пользователь: {user.first_name}")
    else:
        users_db[user.id]["messages"] += 1

# === ОБРАБОТЧИКИ ===
@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    await save_user(message)
    text = f"👋 Привет, {message.from_user.first_name}!\n\n👇 Выбирай кнопку в меню 👇"
    await message.reply(text, reply_markup=get_main_keyboard())

@dp.message_handler(lambda msg: msg.text == "🤣 Шутка")
async def joke_handler(message: types.Message):
    await save_user(message)
    await message.reply(f"🤣 {random.choice(JOKES)}")

@dp.message_handler(lambda msg: msg.text == "📜 Цитата")
async def quote_handler(message: types.Message):
    await save_user(message)
    await message.reply(f"📝 {random.choice(QUOTES)}")

@dp.message_handler(lambda msg: msg.text == "😂 Мем")
async def meme_handler(message: types.Message):
    await save_user(message)
    
    # Пробуем получить картинку
    meme_url = get_meme_image()
    
    if meme_url:
        try:
            # Скачиваем картинку
            response = requests.get(meme_url, timeout=15)
            if response.status_code == 200:
                # Создаем временный файл
                with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                    tmp_file.write(response.content)
                    tmp_path = tmp_file.name
                
                # Отправляем как фото
                photo = open(tmp_path, 'rb')
                await bot.send_photo(message.chat.id, photo, caption="😂 Держи свежий мем!")
                photo.close()
                
                # Удаляем временный файл
                os.unlink(tmp_path)
            else:
                await message.reply(random.choice(TEXT_MEMES))
        except Exception as e:
            print(f"Ошибка: {e}")
            await message.reply(random.choice(TEXT_MEMES))
    else:
        await message.reply(random.choice(TEXT_MEMES))

@dp.message_handler(lambda msg: msg.text == "🔍 Факт")
async def fact_handler(message: types.Message):
    await save_user(message)
    await message.reply(random.choice(FACTS))

@dp.message_handler(lambda msg: msg.text == "👤 Мой профиль")
async def profile_handler(message: types.Message):
    await save_user(message)
    user = message.from_user
    data = users_db.get(user.id, {})
    text = f"👤 **ТВОЙ ПРОФИЛЬ**\n\n📝 Имя: {user.first_name}\n🔰 Username: @{user.username if user.username else 'нет'}\n💬 Сообщений: {data.get('messages', 1)}"
    await message.reply(text)

@dp.message_handler(commands=["menu"])
async def cmd_menu(message: types.Message):
    await save_user(message)
    await message.reply("📱 Меню:", reply_markup=get_main_keyboard())

@dp.message_handler()
async def any_text(message: types.Message):
    await save_user(message)
    await message.reply("Используй кнопки в меню 👇", reply_markup=get_main_keyboard())

# === ВЕБ-СЕРВЕР ДЛЯ RENDER ===
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Бот запущен и работает!"

@app.route('/health')
def health():
    return "OK", 200

def run_bot():
    """Запуск бота в отдельном потоке"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    executor = dp.start_polling()
    loop.run_until_complete(executor)

# === ЗАПУСК ===
if __name__ == "__main__":
    # Запускаем бота в отдельном потоке
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    print("✅ Бот запущен в фоновом потоке")
    
    # Запускаем Flask-сервер
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)