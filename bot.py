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

# Очередь для хранения ID пользователей, которые ждут ключ
user_queue = []

user_client = TelegramClient("user_session", API_ID, API_HASH)
bot_client = TelegramClient("bot_session", API_ID, API_HASH)

@bot_client.on(events.NewMessage(pattern=r'/start'))
async def start_handler(event):
    if event.is_private:
        await event.respond("Привет! Пришли ссылку, я пришлю ключ.")

# 1. Принимаем ссылку от пользователя в твоем боте
@bot_client.on(events.NewMessage)
async def handle_user_link(event):
    if event.is_private and event.text and "http" in event.text:
        user_queue.append(event.chat_id)
        await event.reply("Ищу ключ...")
        try:
            # Шлем ссылку чужому боту с вирт-аккаунта
            await user_client.send_message(OTHER_BOT, event.text)
            print(f"Ссылка от пользователя {event.chat_id} ушла чужому боту.")
        except Exception as e:
            print(f"Ошибка отправки чужому боту: {e}")
            if event.chat_id in user_queue:
                user_queue.remove(event.chat_id)
            await event.reply(f"Ошибка при отправке: {e}")

# 2. Ловим ответ в ЛС вирт-аккаунта и сразу кидаем пользователю
@user_client.on(events.NewMessage)
async def handle_key_response(event):
    if event.is_private:
        sender = await event.get_sender()
        if sender and sender.bot and (sender.username and sender.username.lower() == OTHER_BOT):
            print(f"Получен ответ от чужого бота: {event.text[:30]}...")
            
            # Проверяем, есть ли кто-то в очереди ожидания
            if user_queue:
                target_user = user_queue.pop(0)
                try:
                    # Отправляем ключ пользователю через твоего бота
                    await bot_client.send_message(target_user, event.text)
                    print(f"Ключ успешно доставлен пользователю {target_user}!")
                except Exception as e:
                    print(f"Ошибка при отправке ключа пользователю: {e}")
            else:
                print("Получен ключ, но очередь пуста.")

async def main():
    await user_client.start(phone=PHONE)
    await bot_client.start(bot_token=BOT_TOKEN)
    print("Бот и вирт-аккаунт успешно запущены и слушают!")
    await asyncio.gather(user_client.run_until_disconnected(), bot_client.run_until_disconnected())

if __name__ == "__main__":
    asyncio.run(main())
