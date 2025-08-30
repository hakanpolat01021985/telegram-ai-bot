import os
from telegram.ext import Application, CommandHandler

# BotFather'dan aldığınız API Token'ı buraya girin
# Token'ı artık Render'ın ortam değişkenlerinden alacağız
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# /start komutu geldiğinde çalışacak fonksiyon
async def start(update, context):
    await update.message.reply_text("Merhaba! Hoş geldiniz!")

def main():
    # Telegram botu oluşturma
    application = Application.builder().token(BOT_TOKEN).build()

    # /start komutunu dinlemesi için bir Handler ekleme
    application.add_handler(CommandHandler("start", start))

    # Botu çalıştırma
    application.run_polling()

if __name__ == "__main__":
    main()
