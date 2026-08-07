import asyncio
from telethon import TelegramClient, events
from flask import Flask
import threading

# Настройка веб-сервера для удержания хостинга
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

threading.Thread(target=run_flask, daemon=True).start()

# Данные для авторизации
API_ID = 2496
API_HASH = "8da85b0d5bfe62527e5b244c209159c3"
BOT_TOKEN = "7597650548:AAFFDOmUgNXqGz7VBNcW_xHj315mZq589QQ"
PHONE = "+447407898803"

# Целевой бот
OTHER_BOT = "KrevetkascriptsBy_Bot"
last_user_id = None

# Клиент Telegram (работаем через user_client)
user_client = TelegramClient('user_session', API_ID, API_HASH)

# Обработчик входящих ссылок от тебя
@user_client.on(events.NewMessage(incoming=True))
async def handle_user_link(event):
    global last_user_id
    if event.is_private and event.text and "http" in event.text:
        last_user_id = event.chat_id
        print(f"[LOG] Получена ссылка от пользователя: {event.text}")
        
        try:
            # 1. Отправляем команду /bypass боту
            await user_client.send_message(OTHER_BOT, "/bypass")
            print(f"[LOG] Команда /bypass отправлена")
            
            # Пауза для появления кнопки
            await asyncio.sleep(1.5)

            # 2. Ищем сообщение с кнопкой и нажимаем её
            clicked = False
            async for message in user_client.iter_messages(OTHER_BOT, limit=3):
                if message.buttons:
                    await message.click(0)
                    print(f"[LOG] Кнопка успешно нажата!")
                    clicked = True
                    break
            
            if not clicked:
                print(f"[LOG WARNING] Кнопка не найдена, повтор...")
                await asyncio.sleep(1)
                async for message in user_client.iter_messages(OTHER_BOT, limit=3):
                    if message.buttons:
                        await message.click(0)
                        print(f"[LOG] Кнопка нажата со второй попытки!")
                        break

            # Пауза перед отправкой самой ссылки
            await asyncio.sleep(1)

            # 3. Отправляем ссылку чужому боту
            await user_client.send_message(OTHER_BOT, event.text)
            print(f"[LOG] Ссылка успешно отправлена чужому боту.")

            # 4. Отправляем статус со смайликом в самом конце
            await event.reply("<tg-emoji emoji-id=\"5278305362703835500\">🔗</tg-emoji> <b>Ссылка обрабатывается!</b>", parse_mode='html')

        except Exception as e:
            print(f"[LOG ERROR] Ошибка: {e}")
            await event.reply(f"Ошибка при отправке: {e}")
            
# Исправленный перехват ответа
@user_client.on(events.NewMessage)
async def handle_key_response(event):
    global last_user_id
    if event.is_private:
        sender = await event.get_sender()
        if sender and sender.username == OTHER_BOT:
            message_text = event.text
            if event.reply_markup and not message_text:
                for row in event.reply_markup.rows:
                    for button in row.buttons:
                        message_text += f"\nКнопка: {button.text}"
            
            print(f"[LOG] Пойман ответ от бота! Текст: {message_text}")
            if last_user_id:
                import re
                key_match = re.search(r'FREE_[a-zA-Z0-9]+', message_text)
                if key_match:
                    final_key = key_match.group(0)
                    custom_message = (
                        "<tg-emoji emoji-id=\"5278602437001767574\">🔒</tg-emoji> <b>Успешный обход!</b>\n\n"
                        "<tg-emoji emoji-id=\"5278602437001767574\">🔒</tg-emoji> <b>Твой ключ:</b>\n"
                        f"<code>{final_key}</code>\n\n"
                        "<tg-emoji emoji-id=\"5278305362703835500\">🔗</tg-emoji> <i>Обрабатываю ссылку...</i>\n"
                        "<tg-emoji emoji-id=\"5206476089127372379\">⭐</tg-emoji> <b>Ваш сервис</b>")
                    await user_client.send_message(last_user_id, custom_message, parse_mode='html')
                else:
                    await user_client.send_message(last_user_id, "Ключ не найден в ответе бота.")
                last_user_id = None
              
async def main():
    await user_client.start(phone=PHONE)
    print("Всё запущено, клиент активен.")
    await asyncio.gather(user_client.run_until_disconnected())

if __name__ == "__main__":
    asyncio.run(main())
