import os
import openai
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters

# Ortam değişkenlerinden tokenleri al
TELEGRAM_TOKEN = os.environ["8490762605:AAHNFyHkOEZhgsFReyRKOSQ8exDSlgQnEwY"]
OPENAI_API_KEY = os.environ["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"]

openai.api_key = OPENAI_API_KEY

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    try:
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

    await update.message.reply_text(bot_reply)

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
