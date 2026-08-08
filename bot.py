import asyncio
import re
import threading
from flask import Flask
from telethon import TelegramClient, events

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive!"

threading.Thread(target=lambda: app.run(host="0.0.0.0", port=8080), daemon=True).start()

API_ID = 2040
API_HASH = "b18441a1ff607e10a989891a5462e627"
OTHER_BOT = "KrevetkascriptsBy_Bot"
BOT_TOKEN = "7597650548:AAFFDOmUgNXqGz7VBNcW_xHj315mZq589QQ"

user_client = TelegramClient('user_session', API_ID, API_HASH)
bot_client = TelegramClient('bot_session', API_ID, API_HASH)

pending_requests = [] 

# 1. ОБРАБОТКА ССЫЛКИ ОТ ЮЗЕРА
@bot_client.on(events.NewMessage(incoming=True))
async def handle_user_request(event):
    if event.is_private and event.text and "http" in event.text:
        user_id = event.chat_id
        url = event.text.strip()
        
        # Красивый статус с эмодзи ссылки
        status_msg = await event.reply(
            '<emoji id="5278305362703835500">🔗</emoji> <b>Статус:</b> <i>Обрабатываю ссылку...</i>',
            parse_mode="html"
        )
        pending_requests.append({'user_id': user_id, 'msg_obj': status_msg})
        
        await user_client.send_message(OTHER_BOT, "/bypass")
        await asyncio.sleep(2)
        
        msg = await user_client.get_messages(OTHER_BOT, limit=1)
        if msg and msg[0].buttons:
            await msg[0].click(0)
            await asyncio.sleep(2)
        
        await user_client.send_message(OTHER_BOT, url)

# 2. УНИВЕРСАЛЬНЫЙ СЛУШАТЕЛЬ ОТВЕТА
@user_client.on(events.MessageEdited(chats=OTHER_BOT))
@user_client.on(events.NewMessage(chats=OTHER_BOT))
async def handle_all_updates(event):
    msg_text = event.raw_text or event.text or ""
    if event.reply_markup:
        for row in event.reply_markup.rows:
            for btn in row.buttons:
                msg_text += f" {btn.text}"
    
    key_match = re.search(r"FREE_[A-Za-z0-9_]+", msg_text)
    
    if key_match and pending_requests:
        final_key = key_match.group(0)
        req = pending_requests.pop(0)
        
        # Полный текст и премиум-эмодзи, как на первом скрине
        new_text = (
            f'<emoji id="5278602437001767574">🔐</emoji> <b>Успешный обход!</b>\n\n'
            f'<emoji id="5276262671962892944">🛡</emoji> <b>Твой ключ:</b>\n'
            f'<code>{final_key}</code>\n\n'
            f'<emoji id="5278305362703835500">🔗</emoji> <i>Обрабатываю ссылку...</i>\n'
            f'<emoji id="5206476089127372379">⭐️</emoji> <b>Ваш сервис</b>'
        )
        try:
            await bot_client.edit_message(req['user_id'], req['msg_obj'].id, new_text, parse_mode="html")
        except Exception as e:
            print(f"[ERROR EDIT] {e}")

async def main():
    await user_client.start()
    await bot_client.start(bot_token=BOT_TOKEN)
    print("--- БОТ ЗАПУЩЕН ---")
    await asyncio.gather(user_client.run_until_disconnected(), bot_client.run_until_disconnected())

if __name__ == "__main__":
    asyncio.run(main())
