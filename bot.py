import telebot
from telebot import types
import random
import string
import time
import base64
import requests
import os

from telebot import apihelper
apihelper.proxy = {}   # отключаем прокси

# ===== ЗАГРУЖАЕМ ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ =====
API_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [7487527727]

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = os.getenv("GITHUB_REPO")            # например: "username/repo"
FILE_PATH = os.getenv("GITHUB_FILE")       # например: "cache.bin"

last_gen_time = {}

bot = telebot.TeleBot(API_TOKEN)

# ===== генерация ключа =====
def generate_key():
    suffix = "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(4))
    key = f"erktap{suffix}"
    expire = int(time.time()) + 12 * 3600
    return f"{key}:{expire}"

# ===== SHA файла =====
def get_file_sha():
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        return r.json()["sha"], r.json()["content"]
    return None, None

# ===== обновление файла =====
def update_keys(new_entry):
    sha, content_b64 = get_file_sha()
    if not sha:
        return False, "Не удалось получить SHA"

    old = base64.b64decode(content_b64).decode("utf-8")
    new = old + f"\n{new_entry}"

    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    data = {
        "message": "update",
        "content": base64.b64encode(new.encode("utf-8")).decode("utf-8"),
        "sha": sha
    }
    r = requests.put(url, headers=headers, json=data)
    return r.status_code == 200, r.text

# ===== /start =====
@bot.message_handler(commands=["start"])
def start(message):
    markup = types.InlineKeyboardMarkup()
    for channel in [
        {'url': 'https://t.me/+mQbQzEDyPTZhMmJi'},
        {'url': 'https://t.me/ErkoshaTop'},
        {'url': 'https://t.me/+SrUWB7AuRJs0ZTQ5'},
        {'url': 'https://t.me/+2Akzj3ro2EU2NGUy'}
    ]:
        markup.add(types.InlineKeyboardButton("Подписаться на канал", url=channel["url"]))
    markup.add(types.InlineKeyboardButton("Проверить подписку", callback_data="check_subscription"))

    bot.send_message(
        message.chat.id,
        "Привет! Подпишись на все каналы и получи ключ (Chillow).",
        reply_markup=markup
    )

# ===== проверка подписки =====
@bot.callback_query_handler(func=lambda call: call.data == "check_subscription")
def check_subscription(call):
    user_id = call.from_user.id
    now = time.time()

    # лимит
    if user_id in last_gen_time and now - last_gen_time[user_id] < 12 * 3600:
        remaining = int(12 * 3600 - (now - last_gen_time[user_id]))
        bot.send_message(
            call.message.chat.id,
            f"⏳ Новый ключ через {remaining // 3600} ч. {(remaining % 3600)//60} мин."
        )
        return

    # Проверка подписок
    all_subscribed = True
    for channel in [-1001618709375, "@ErkoshaTop", "@SigmaApk", "@ApkNeetMod"]:
        try:
            member = bot.get_chat_member(channel, user_id)
            if member.status in ["left", "kicked"]:
                all_subscribed = False
                break
        except:
            pass

    if all_subscribed:
        new_entry = generate_key()
        key, expire = new_entry.split(":")

        ok, resp = update_keys(new_entry)
        if ok:
            bot.send_message(
                call.message.chat.id,
                f"✅ Спасибо!\nВаш ключ: `{key}`\nРаботает 12 часов.\n"
                f"Обновление списка ключей после перезахода в чит.",
                parse_mode="Markdown"
            )
            last_gen_time[user_id] = now
        else:
            bot.send_message(call.message.chat.id, "❌ Ошибка записи")

    else:
        bot.send_message(call.message.chat.id, "❌ Подпишитесь на все каналы.")

bot.polling()