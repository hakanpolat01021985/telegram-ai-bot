import os
import telegram
from telegram.ext import Updater, CommandHandler

# BotFather'dan aldığınız API Token'ı buraya girin
BOT_TOKEN = os.environ["BOT_TOKEN"]

# /start komutu geldiğinde çalışacak fonksiyon
async def start(update, context):
    await update.message.reply_text("Merhaba! Hoş geldiniz!")

def main():
    # Telegram botu oluşturma
    application = telegram.Application.builder().token(BOT_TOKEN).build()
    
    # /start komutunu dinlemesi için bir Handler ekleme
    application.add_handler(CommandHandler("start", start))
    
    # Botu çalıştırma
    application.run_polling()

if __name__ == "__main__":
    main()
