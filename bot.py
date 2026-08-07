import os
import threading
from flask import Flask
import asyncio
from telethon import TelegramClient, events

app = Flask(name)

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

OTHER_BOT = "robloxbypass"  # пишем в нижнем регистре для надежности
pending_requests = []

user_client = TelegramClient("user_session", API_ID, API_HASH)
bot_client = TelegramClient("bot_session", API_ID, API_HASH)

@bot_client.on(events.NewMessage(pattern=r'/start'))
async def start_handler(event):
    if event.is_private:
        await event.respond(
            "Привет! Я бот для обхода ссылок.\n\n"
            "Пришли мне ссылку, и я моментально пришлю тебе ключ!"
        )

@bot_client.on(events.NewMessage)
async def handle_user_link(event):
    if event.is_private and event.text and "http" in event.text:
        pending_requests.append(event.chat_id)
        await event.reply("Ищу ключ...")
        try:
            await user_client.send_message(OTHER_BOT, "/bypass " + event.text)
        except Exception as e:
            print(f"Error sending message: {e}")

@user_client.on(events.NewMessage)
async def handle_key_response(event):
    sender = await event.get_sender()
    if not sender or getattr(sender, 'username', '').lower() != OTHER_BOT:
        return

    response_text = event.text or event.message.caption or ""
    if not response_text:
        return

    if "Как использовать" in response_text or "Используйте" in response_text:
        return

    if "FREE_" in response_text and pending_requests:
        try:
            part = response_text.split("FREE_")[1]
            key_raw = part.split("Потребовалось")[0]
            final_key = "FREE_" + key_raw.strip()
            
            target_user = pending_requests.pop(0)
            await bot_client.send_message(target_user, final_key)
        except Exception as e:
            print(f"Parse error: {e}")

async def main():
    await user_client.start(phone=PHONE)
    await bot_client.start(bot_token=BOT_TOKEN)
    await asyncio.gather(
        user_client.run_until_disconnected(),
        bot_client.run_until_disconnected()
    )

if name == "main":
    asyncio.run(main())
