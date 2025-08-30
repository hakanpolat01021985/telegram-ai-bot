import os
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from openai import OpenAI

# OpenAI API anahtarını Render'ın ortam değişkenlerinden al
openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# /start komutu
async def start(update, context):
    await update.message.reply_text("Merhaba! Nasıl yardımcı olabilirim?")

# Mesajlara ChatGPT ile yanıt verme
async def chatgpt_reply(update, context):
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Sen bir müşteri hizmetleri temsilcisisin. Müşterilerin sorunlarına yardımcı olmaya çalış."},
                {"role": "user", "content": update.message.text}
            ]
        )
        reply = response.choices[0].message.content
        await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text(f"Bir hata oluştu: {e}")

def main():
    bot_token = os.environ.get("BOT_TOKEN")
    application = Application.builder().token(bot_token).build()
    
    # Komutları ve mesajları dinleyen handler'lar
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chatgpt_reply))
    
    application.run_polling()

if __name__ == "__main__":
    main()
