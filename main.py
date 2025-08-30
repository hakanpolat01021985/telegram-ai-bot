import os
import telegram
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import google.generativeai as genai

# Gemini API anahtarını Render'ın ortam değişkenlerinden al
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

# /start komutu
async def start(update, context):
    await update.message.reply_text("Merhaba! Nasıl yardımcı olabilirim?")

# Mesajlara Gemini ile yanıt verme
async def gemini_reply(update, context):
    try:
        # Mesajı Gemini'ye gönder ve yanıtı al
        response = model.generate_content(update.message.text)
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text(f"Bir hata oluştu: {e}")

def main():
    bot_token = os.environ.get("BOT_TOKEN")
    application = Application.builder().token(bot_token).build()
    
    # Komut ve mesaj handler'larını ekle
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, gemini_reply))
    
    application.run_polling()

if __name__ == "__main__":
    main()
