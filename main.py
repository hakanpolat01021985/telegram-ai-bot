import os
import google.generativeai as genai
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes
)
import asyncio

# ================== AYARLAR ==================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini yapılandırması
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# Şirket bilgilerini modele öğretme
COMPANY_INFO = """
Sen bir müşteri destek botusun.
Şirket: Hiper Televizyon (IPTV hizmeti).
Müşterilere IPTV kanalları, paketler, fiyatlar ve kurulum hakkında yardımcı olabilirsin.
Eğer kullanıcı teknik destek isterse 'Teknik ekibimiz en kısa sürede sizinle iletişime geçecektir.' de.
Eğer fiyat sorulursa, kesin fiyat vermek yerine 'Size en uygun paketlerimizi müşteri temsilcimiz paylaşabilir.' de.
Her zaman kibar ve profesyonel cevap ver.
"""

# Kullanıcı zaman takibi (AFK kontrolü)
last_message_time = {}

# ================== KOMUTLAR ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    last_message_time[user_id] = asyncio.get_event_loop().time()
    await update.message.reply_text(
        "👋 Merhaba, Hiper Televizyon müşteri destek botuna hoş geldiniz!\n"
        "Nasıl yardımcı olabilirim?"
    )

async def yardim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 Kullanabileceğiniz komutlar:\n"
        "/yardim - Komutları gör\n"
        "/canli - Canlı müşteri temsilcisine bağlanma talebi\n"
    )

async def canli(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ Talebiniz alındı. Canlı müşteri temsilcimiz en kısa sürede sizinle iletişime geçecektir."
    )

# ================== MESAJ CEVAPLAMA ==================
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    last_message_time[user_id] = asyncio.get_event_loop().time()

    user_message = update.message.text

    # Gemini’ye soruyu şirket bilgileriyle gönder
    response = model.generate_content(f"{COMPANY_INFO}\n\nMüşteri: {user_message}")
    await update.message.reply_text(response.text)

# ================== OTOMATİK KAPANIŞ ==================
async def afk_checker(app: Application):
    while True:
        now = asyncio.get_event_loop().time()
        for user_id, last_time in list(last_message_time.items()):
            if now - last_time > 300:  # 5 dakika
                chat = await app.bot.get_chat(user_id)
                await chat.send_message("⌛ Görüşme sona erdi. Tekrar yazmak için /start kullanabilirsiniz.")
                del last_message_time[user_id]
        await asyncio.sleep(60)

# ================== ANA UYGULAMA ==================
def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("yardim", yardim))
    app.add_handler(CommandHandler("canli", canli))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))

    # AFK kontrolünü arka planda çalıştır
    app.job_queue.run_once(lambda ctx: asyncio.create_task(afk_checker(app)), 1)

    print("🚀 Bot çalışıyor...")
    app.run_polling()

if __name__ == "__main__":
    main()
