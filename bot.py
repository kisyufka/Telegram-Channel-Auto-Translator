import telebot
from deep_translator import GoogleTranslator

BOT_TOKEN = "ВАШ_ТОКЕН_БОТА" 
CHANNEL_ID = -1003661484159

bot = telebot.TeleBot(BOT_TOKEN)

def translate_text(text, source_lang='ru', target_lang='en'): #Тут Выбор Языка
    try:
        translator = GoogleTranslator(source=source_lang, target=target_lang)
        translated = translator.translate(text)
        return translated
    except Exception as e:
        print(f"Ошибка перевода: {e}")
        return text

@bot.channel_post_handler(content_types=['text'])
def handle_channel_post(message):
    try:
        if message.chat.id != CHANNEL_ID:
            return
        original_text = message.text
        translated_text = translate_text(original_text)
        formatted_text = (
            f"<b>English version:</b>\n"
            f"<blockquote>{translated_text}</blockquote>\n\n"
            f"<b>Русская версия:</b>\n"
            f"<blockquote>{original_text}</blockquote>"
        )
        bot.edit_message_text(
            chat_id=CHANNEL_ID,
            message_id=message.message_id,
            text=formatted_text,
            parse_mode='HTML'
        )
        print(f"Сообщение #{message.message_id} отредактировано: {original_text[:50]}...")
    except Exception as e:
        print(f"Ошибка при редактировании: {e}")
@bot.message_handler(func=lambda message: message.chat.id == CHANNEL_ID and message.text)
def handle_channel_message(message):
    handle_channel_post(message)
if __name__ == "__main__":
    print(f"Бот запущен для канала ID: {CHANNEL_ID}")
    print("Ожидание новых постов...")
    bot.polling(none_stop=True, interval=0)
