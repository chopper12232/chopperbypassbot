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

# Клиенты Телеграм
user_client = TelegramClient("user_session", API_ID, API_HASH)
bot_client = TelegramClient("bot_session", API_ID, API_HASH)

# Обработчик команды /start для твоего основного бота
@bot_client.on(events.NewMessage(pattern=r'/start'))
async def start_handler(event):
    if event.is_private:
        await event.respond("Привет! Пришли ссылку, я пришлю ключ.")

# Обработчик входящих ссылок от пользователей с нажатием кнопки
@bot_client.on(events.NewMessage)
async def handle_user_link(event):
    global last_user_id
    if event.is_private and event.text and "http" in event.text:
        last_user_id = event.chat_id
        print(f"[LOG] Получена ссылка от пользователя ID: {last_user_id}")
        await event.reply("Ищу ключ...")
        try:
            # 1. Отправляем команду /bypass боту
            await user_client.send_message(OTHER_BOT, "/bypass")
            
            # Пауза, чтобы бот успел прислать ответ с кнопкой
            await asyncio.sleep(1)
            
            # 2. Ищем сообщение от бота с кнопкой и нажимаем её
            async for message in user_client.iter_messages(OTHER_BOT, limit=3):
                if message.buttons:
                    await message.click(0)
                    print(f"[LOG] Кнопка успешно нажата!")
                    break
            
            # 3. Отправляем саму ссылку следующим сообщением
            await user_client.send_message(OTHER_BOT, event.text)
            print(f"[LOG] Ссылка успешно отправлена чужому боту.")
            
        except Exception as e:
            print(f"[LOG ERROR] Ошибка при взаимодействии с ботом: {e}")
            await event.reply(f"Ошибка при отправке: {e}")

# Исправленный перехват ответа
@user_client.on(events.NewMessage)
async def handle_key_response(event):
    global last_user_id
    if event.is_private:
        sender = await event.get_sender()
        # Проверяем, что сообщение от нужного бота
        if sender and sender.username == OTHER_BOT:
            # Пытаемся получить текст из самого сообщения
            message_text = event.text
            
            # Если основной текст пустой или короткий, пробуем достать из кнопок
            if not message_text or len(message_text) < 10:
                if event.reply_markup:
                    for row in event.reply_markup.rows:
                        for button in row.buttons:
                            # Часто боты прячут результат в callback_data или текст кнопки
                            message_text += f"\nКнопка: {button.text}"
            
            print(f"[LOG] Пойман ответ от бота! Текст: {message_text}")
            
            if last_user_id:
                try:
                    await bot_client.send_message(last_user_id, message_text)
                    print(f"[LOG] Ключ успешно отправлен пользователю {last_user_id}")
                except Exception as e:
                    print(f"[LOG ERROR] Не удалось отправить ключ: {e}")
                last_user_id = None

async def main():
    await user_client.start(phone=PHONE)
    await bot_client.start(bot_token=BOT_TOKEN)
    print("Всё запущено, клиенты активны.")
    await asyncio.gather(user_client.run_until_disconnected(), bot_client.run_until_disconnected())

if __name__ == "__main__":
    asyncio.run(main())
