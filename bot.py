import asyncio
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

# Данные для юзербота (британский аккаунт)
API_ID = 2040
API_HASH = "b18441a1ff607e10a989891a5462e627"
OTHER_BOT = "KrevetkascriptsBy_Bot"

# ТОКЕН ТВОЕГО БОТА
BOT_TOKEN = "7597650548:AAFFDOmUgNXqGz7VBNcW_xHj315mZq589QQ"

# Инициализация двух клиентов
user_client = TelegramClient('user_session', API_ID, API_HASH)
bot_client = TelegramClient('bot_session', API_ID, API_HASH)

pending_requests = [] 

# 1. ОСНОВНОЙ БОТ (Общение с пользователями)
@bot_client.on(events.NewMessage(incoming=True))
async def handle_user_request(event):
    if event.is_private and event.text and "http" in event.text:
        user_id = event.chat_id
        url = event.text.strip()
        
        status_msg = await event.reply(
            "🔗 <b>Статус:</b> <i>Обрабатываю ссылку...</i>",
            parse_mode="html"
        )
        
        pending_requests.append({'user_id': user_id, 'msg_obj': status_msg})
        
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
            await user_client.send_message(OTHER_BOT, url)
        except Exception as e:
            print(f"[ERROR] {e}")

# 2. ЮЗЕРБОТ (Скрытый курьер)
@user_client.on(events.NewMessage(incoming=True))
async def handle_key_response(event):
    if event.is_private and event.sender_id and (await event.get_sender()).username == OTHER_BOT:
        message_text = event.text or ""
        if event.reply_markup and not message_text:
            for row in event.reply_markup.rows:
                for button in row.buttons:
                    message_text += f"\n{button.text}"

        print(f"[LOG] Ключ получен: {message_text}")
        
        if pending_requests:
            key_match = re.search(r"FREE_[a-zA-Z0-9]+", message_text)
            req = pending_requests.pop(0)
            user_id = req['user_id']
            status_msg = req['msg_obj']

            if key_match:
                final_key = key_match.group(0)
                new_text = f"🔐 <b>Статус: Успешный обход!</b>\n\n<code>{final_key}</code>\n\n⭐️ <b>Ваш сервис</b>"
                await bot_client.edit_message(user_id, status_msg.id, new_text, parse_mode="html")
            else:
                await bot_client.edit_message(user_id, status_msg.id, "❌ <b>Статус:</b> Ключ не найден.", parse_mode="html")

async def main():
    print("Система запущена...")
    await user_client.start()
    await bot_client.start(bot_token=BOT_TOKEN)
    await asyncio.gather(user_client.run_until_disconnected(), bot_client.run_until_disconnected())

if __name__ == "__main__":
    asyncio.run(main())
