import os
import threading
from flask import Flask
import asyncio
from telethon import TelegramClient, events

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_flask, daemon=True).start()

API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
PHONE = os.environ.get("PHONE", "")

OTHER_BOT = "getkey"
pending_requests = []

user_client = TelegramClient("user_session", API_ID, API_HASH)
bot_client = TelegramClient("bot_session", API_ID, API_HASH)

@bot_client.on(events.NewMessage(pattern=r'/start'))
async def start_handler(event):
    if event.is_private:
        await event.respond("Привет! Пришли ссылку, я пришлю ключ.")

@bot_client.on(events.NewMessage)
async def handle_user_link(event):
    if event.is_private and event.text and "http" in event.text:
        pending_requests.append(event.chat_id)
        await event.reply("Ищу ключ...")
        try:
            print(f"DEBUG: Пытаюсь отправить ссылку боту {OTHER_BOT}...")
            await user_client.send_message(OTHER_BOT, "/bypass " + event.text)
            print("DEBUG: Сообщение успешно отправлено!")
        except Exception as e:
            print(f"DEBUG: Ошибка при отправке: {e}")
            await event.reply(f"Ошибка при отправке: {e}")

@user_client.on(events.NewMessage)
async def handle_key_response(event):
    sender = await event.get_sender()
    if sender and getattr(sender, 'username', '').lower() == OTHER_BOT:
        print(f"DEBUG: Получен ответ от {OTHER_BOT}: {event.text[:50]}...")
        if "FREE_" in event.text and pending_requests:
            target_user = pending_requests.pop(0)
            await bot_client.send_message(target_user, event.text)
            print("DEBUG: Ключ успешно отправлен пользователю!")

async def main():
    await user_client.start(phone=PHONE)
    await bot_client.start(bot_token=BOT_TOKEN)
    print("DEBUG: Бот запущен и готов к работе!")
    await asyncio.gather(user_client.run_until_disconnected(), bot_client.run_until_disconnected())

if __name__ == "__main__":
    asyncio.run(main())
