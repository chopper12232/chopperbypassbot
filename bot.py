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
last_user_id = None

user_client = TelegramClient("user_session", API_ID, API_HASH)
bot_client = TelegramClient("bot_session", API_ID, API_HASH)

@bot_client.on(events.NewMessage(pattern=r'/start'))
async def start_handler(event):
    if event.is_private:
        await event.respond("Привет! Пришли ссылку, я пришлю ключ.")

@bot_client.on(events.NewMessage)
async def handle_user_link(event):
    global last_user_id
    if event.is_private and event.text and "http" in event.text:
        last_user_id = event.chat_id
        print(f"[LOG] Получена ссылка от пользователя ID: {last_user_id}")
        await event.reply("Ищу ключ...")
        try:
            await user_client.send_message(OTHER_BOT, "/bypass " + event.text)
            print(f"[LOG] Успешно отправлено чужому боту от имени вирт-аккаунта.")
        except Exception as e:
            print(f"[LOG ERROR] Ошибка отправки чужому боту: {e}")
            await event.reply(f"Ошибка при отправке: {e}")

@user_client.on(events.NewMessage)
async def handle_key_response(event):
    global last_user_id
    if event.is_private:
        sender = await event.get_sender()
        # Выводим в лог вообще каждое входящее сообщение в ЛС вирт-аккаунта, чтобы проверить, видит ли он его
        if sender:
            print(f"[LOG USER_CLIENT] Новое сообщение в ЛС от: {getattr(sender, 'username', 'unknown')} | Текст: {event.text[:40]}")
            
        if sender and sender.bot and (sender.username and sender.username.lower() == OTHER_BOT):
            print(f"[LOG] ПОЙМАЛ ОТВЕТ ОТ ЦЕЛЕВОГО БОТА!")
            if last_user_id:
                try:
                    await bot_client.send_message(last_user_id, event.text)
                    print(f"[LOG] Ключ успешно отправлен пользователю {last_user_id}!")
                    last_user_id = None
                except Exception as e:
                    print(f"[LOG ERROR] Не удалось отправить ключ пользователю: {e}")
            else:
                print("[LOG WARNING] Ключ получен, но last_user_id пуст (никто не запрашивал или сбросился).")

async def main():
    await user_client.start(phone=PHONE)
    await bot_client.start(bot_token=BOT_TOKEN)
    print("Всё запущено, клиенты активны.")
    await asyncio.gather(user_client.run_until_disconnected(), bot_client.run_until_disconnected())

if __name__ == "__main__":
    asyncio.run(main())
