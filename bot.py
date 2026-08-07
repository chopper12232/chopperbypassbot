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
    # Достаем текст, даже если он пришел под картинкой (caption)
    response_text = event.text or event.message.caption or ""
    
    # Пропускаем инструкции
    if "Как использовать" in response_text or "Используйте" in response_text:
        return

    if pending_requests and response_text:
        target_user = pending_requests.pop(0)
        await bot_client.send_message(target_user, response_text)

    # Если пришёл реальный ключ или результат
    if pending_requests:
        target_user = pending_requests.pop(0)
        await bot_client.send_message(target_user, text)
        
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
