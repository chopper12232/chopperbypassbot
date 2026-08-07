import os
import threading
from flask import Flask

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

threading.Thread(target=run, daemon=True).start()
import asyncio
from telethon import TelegramClient, events
# Берём данные из Environment Variables на Render
API_ID = int(os.environ.get("API_ID", 2040))
API_HASH = os.environ.get("API_HASH", "b18441a1ff607e10a989891a5462e627")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "7597650548:AAFFDOmUgNXqGz7VBNcW_xHj315mZq589QQ")
PHONE = os.environ.get("PHONE", "+447407898803")
OTHER_BOT = os.environ.get("OTHER_BOT", "@getkey")

# Клиент юзербота (от чьего имени запрашиваем)
user_client = TelegramClient("user_session", API_ID, API_HASH)
# Клиент основного бота (который отвечает пользователю)
bot_client = TelegramClient("bot_session", API_ID, API_HASH)

# Очередь ожидающих пользователей: {user_id_кто_ждет: timestamp}
pending_requests = []

@bot_client.on(events.NewMessage(pattern=r'/start'))
async def start_handler(event):
    await event.respond(
        "👋 **Привет! Я бот для обхода ссылок.\n\n"
        "⚡ Пришли мне ссылку, и я моментально пришлю тебе ключ!"
    )

@bot_client.on(events.NewMessage)
async def handle_user_link(event):
    if event.is_private and event.text and "http" in event.text:
        pending_requests.append(event.chat_id)
        await event.reply("⏳ Ищу ключ...")
        # Пересылаем ссылку в сторонний бот от имени аккаунта
        await user_client.send_message(OTHER_BOT, "/bypass " + event.text)

@user_client.on(events.NewMessage(chats=OTHER_BOT))
async def handle_key_response(event):
    # Берем текст или подпись под картинкой
    response_text = event.text or event.message.caption or ""
    
    # Игнорируем инструкции стороннего бота
    if "Как использовать" in response_text or "Используйте" in response_text:
        return

    # Ищем ключ, если он есть
    if "FREE_" in response_text and pending_requests:
        # Разбиваем строку, чтобы найти кусок с FREE_
        # Мы берем все, что идет после FREE_, до ближайшего пробела или конца строки
        key_part = response_text.split("FREE_")[1].split()[0]
        final_key = "FREE_" + key_part
        
        target_user = pending_requests.pop(0)
        # Отправляем пользователю ТОЛЬКО чистый ключ
        await bot_client.send_message(target_user, final_key)

 
async def main():
    print("✅ Подключаем аккаунт...")
    await user_client.start(phone=PHONE)
    
    print("✅ Подключаем бота...")
    await bot_client.start(bot_token=BOT_TOKEN)
    
    print("✅ Бот запущен!")
    await asyncio.gather(
        user_client.run_until_disconnected(),
        bot_client.run_until_disconnected()
    )

if __name__ == "__main__":
    asyncio.run(main())
