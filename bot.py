import asyncio
import os
import re
import threading
from flask import Flask
from telethon import TelegramClient, events

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive!"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

threading.Thread(target=run_flask, daemon=True).start()

API_ID = 2040
API_HASH = "b18441a1ff607e10a989891a5462e627"
OTHER_BOT = "KrevetkascriptsBy_Bot"
last_user_id = None

user_client = TelegramClient('user_session', API_ID, API_HASH)

@user_client.on(events.NewMessage(incoming=True))
async def handle_user_link(event):
    global last_user_id
    if event.is_private and event.text and "http" in event.text:
        last_user_id = event.chat_id
        print(f"[LOG] Получена ссылка: {event.text}")
        try:
            await user_client.send_message(OTHER_BOT, "/bypass")
            await asyncio.sleep(1.5)

            clicked = False
            async for message in user_client.iter_messages(OTHER_BOT, limit=3):
                if message.buttons:
                    await message.click(0)
                    clicked = True
                    break

            if not clicked:
                await asyncio.sleep(1)
                async for message in user_client.iter_messages(OTHER_BOT, limit=3):
                    if message.buttons:
                        await message.click(0)
                        break

            await asyncio.sleep(1)
            await user_client.send_message(OTHER_BOT, event.text)

            await event.reply(
                '<tg-emoji emoji-id="5278305362703835500">🔗</tg-emoji>'
                " <b>Ссылка обрабатывается!</b>",
                parse_mode="html"
            )
        except Exception as e:
            print(f"[LOG ERROR] {e}")

@user_client.on(events.NewMessage)
async def handle_key_response(event):
    global last_user_id
    if event.is_private:
        sender = await event.get_sender()
        if sender and sender.username == OTHER_BOT:
            message_text = event.text or ""
            if event.reply_markup and not message_text:
                for row in event.reply_markup.rows:
                    for button in row.buttons:
                        message_text += f"\nКнопка: {button.text}"

            print(f"[LOG] Пойман ответ от бота: {message_text}")
            if last_user_id:
                key_match = re.search(r"FREE_[a-zA-Z0-9]+", message_text)
                if key_match:
                    final_key = key_match.group(0)
                    custom_message = (
                        '<tg-emoji emoji-id="5278602437001767574">🔐</tg-emoji>'
                        " <b>Успешный обход!</b>\n\n<code>"
                        f"{final_key}</code>\n\n"
                        '<tg-emoji emoji-id="5278305362703835500">🔗</tg-emoji>'
                        " <i>Обрабатываю ссылку...</i>\n<tg-emoji"
                        ' emoji-id="5206476089127372379">⭐️</tg-emoji> <b>Ваш сервис</b>'
                    )
                    await user_client.send_message(last_user_id, custom_message, parse_mode="html")
                else:
                    await user_client.send_message(last_user_id, "Ключ не найден в ответе бота.")
                last_user_id = None

async def main():
    print("Инициализация Telegram клиента...")
    await user_client.start()
    print("Бот успешно запущен и работает!")
    await user_client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
