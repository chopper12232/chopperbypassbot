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

# Переменная для хранения ID пользователя, который последним запросил ключ
last_user_id = None

user_client = TelegramClient("user_session", API_ID, API_HASH)
bot_client = TelegramClient("bot_session", API_ID, API_HASH)

@bot_client.on(events.NewMessage(pattern=r'/start'))
async def start_handler(event):
    if event.is_private:
        await event.respond("Привет! Пришли ссылку, я пришлю ключ.")

# 1. Пользователь пишет твоему боту
@bot_client.on(events.NewMessage)
async def handle_user_link(event):
    global last_user_id
    if event.is_private and event.text and "http" in event.text:
        last_user_id = event.chat_id
        await event.reply("Ищу ключ...")
        try:
            # Шлем с вирт-аккаунта запрос чужому боту
            await user_client.send_message(OTHER_BOT, "/bypass " + event.text)
            print(f"Запрос ушел чужому боту для пользователя {last_user_id}")
        except Exception as e:
            print(f"Ошибка отправки: {e}")
            await event.reply(f"Ошибка при отправке: {e}")

# 2. Вирт-аккаунт получает ответ в ЛС от чужого бота
@user_client.on(events.NewMessage)
async def handle_key_response(event):
    global last_user_id
    if event.is_private:
        sender = await event.get_sender()
        # Проверяем, что это ответ именно от целевого бота
        if sender and sender.bot and (sender.username and sender.username.lower() == OTHER_BOT):
            print(f"Вирт-аккаунт поймал ответ: {event.text[:30]}...")
            if last_user_id:
                try:
                    # Пересылаем полученный ключ обратно пользователю через твоего бота
                    await bot_client.send_message(last_user_id, event.text)
                    print(f"Ключ успешно переслан пользователю {last_user_id}!")
                    last_user_id = None  # Сбрасываем ID после отправки
                except Exception as e:
                    print(f"Ошибка отправки пользователю: {e}")
            else:
                print("Получен ключ, но получатель (last_user_id) не найден.")

async def main():
    await user_client.start(phone=PHONE)
    await bot_client.start(bot_token=BOT_TOKEN)
    print("Всё запущено и работает!")
    await asyncio.gather(user_client.run_until_disconnected(), bot_client.run_until_disconnected())

if __name__ == "__main__":
    asyncio.run(main())
