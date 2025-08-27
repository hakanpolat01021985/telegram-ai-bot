import os
import openai
from telegram.ext import Updater, MessageHandler, Filters

# Ortam değişkenlerinden tokenleri al
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

openai.api_key = OPENAI_API_KEY

def handle_message(update, context):
    user_message = update.message.text

    try:
        # OpenAI'ye mesaj gönder
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Sen müşteri destek asistanısın, kibar ve anlaşılır cevaplar ver."},
                {"role": "user", "content": user_message}
            ]
        )
        bot_reply = response["choices"][0]["message"]["content"]
    except Exception as e:
        bot_reply = f"Hata oluştu: {str(e)}"

    update.message.reply_text(bot_reply)

def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
