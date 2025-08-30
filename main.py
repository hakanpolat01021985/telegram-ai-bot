import os
import logging
from flask import Flask, request, jsonify
import telegram
from telegram import Update, Bot
from telegram.ext import Dispatcher, MessageHandler, Filters, CallbackContext
import google.generativeai as genai

# Flask uygulamasını oluştur
app = Flask(__name__)

# Loglama ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Çevresel değişkenler
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
WEBHOOK_URL = os.environ.get('WEBHOOK_URL')

# Gemini AI yapılandırması - GEMINI 2.5 FLASH
genai.configure(api_key=GEMINI_API_KEY)

# Gemini 2.5 Flash modelini kullan
generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 1024,
}

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
]

# Gemini 2.5 Flash modelini oluştur
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    generation_config=generation_config,
    safety_settings=safety_settings
)

# Bot ve dispatcher oluştur
bot = Bot(token=TELEGRAM_TOKEN)
dispatcher = Dispatcher(bot, None, workers=0)

# Konuşma geçmişini saklamak için basit bir sözlük
conversation_history = {}

def gemini_response(user_id, prompt):
    """Gemini 2.5 Flash'tan yanıt al"""
    try:
        # Konuşma geçmişini al veya oluştur
        if user_id not in conversation_history:
            conversation_history[user_id] = model.start_chat(history=[])
        
        # Gemini'ye mesaj gönder ve yanıt al
        response = conversation_history[user_id].send_message(prompt)
        return response.text
        
    except Exception as e:
        logger.error(f"Gemini hatası: {e}")
        return "Üzgünüm, bir hata oluştu. Lütfen daha sonra tekrar deneyin."

def handle_message(update: Update, context: CallbackContext):
    """Gelen mesajları işle"""
    try:
        message = update.message
        user_id = message.from_user.id
        text = message.text
        
        logger.info(f"Gelen mesaj: {text} - Kullanıcı: {user_id}")
        
        # Gemini'den yanıt al
        response = gemini_response(user_id, text)
        
        # Kullanıcıya yanıt gönder (Telegram mesaj sınırına dikkat ederek)
        if len(response) > 4096:
            for x in range(0, len(response), 4096):
                message.reply_text(response[x:x+4096])
        else:
            message.reply_text(response)
        
    except Exception as e:
        logger.error(f"Mesaj işleme hatası: {e}")
        try:
            message.reply_text("Bir hata oluştu. Lütfen daha sonra tekrar deneyin.")
        except:
            pass

# /start komutu için handler
def start(update: Update, context: CallbackContext):
    """Kullanıcıyı karşılayan mesaj"""
    welcome_text = """
    🤖 Merhaba! Ben Gemini 2.5 Flash destekli müşteri hizmetleri botuyum.
    
    Nasıl yardımcı olabilirim? Sorunuzu iletebilirsiniz.
    """
    update.message.reply_text(welcome_text)

# /help komutu için handler
def help_command(update: Update, context: CallbackContext):
    """Yardım mesajı gönder"""
    help_text = """
    🤖 Yardım Menüsü:
    
    • Sadece sorunuzu yazın, ben yanıtlamaya çalışayım.
    • Doğal dilde iletişim kurabiliriz.
    • Karmaşık sorularınızı basitçe ifade edebilirsiniz.
    
    Örnek sorular:
    - "Ürün iade politikası nedir?"
    - "Siparişim nerede?"
    - "Teknik destek almak istiyorum"
    """
    update.message.reply_text(help_text)

# Komut işleyicileri ekle
from telegram.ext import CommandHandler
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("help", help_command))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

@app.route('/webhook', methods=['POST'])
def webhook():
    """Telegram webhook endpoint"""
    try:
        # Gelen update'i al
        update = Update.de_json(request.get_json(force=True), bot)
        
        # Update'i dispatcher'a ileterek işle
        dispatcher.process_update(update)
        
        return jsonify(success=True)
    except Exception as e:
        logger.error(f"Webhook hatası: {e}")
        return jsonify(success=False), 500

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    """Webhook'u ayarla"""
    try:
        webhook_url = f"{WEBHOOK_URL}/webhook"
        success = bot.set_webhook(webhook_url)
        return jsonify(success=success, url=webhook_url)
    except Exception as e:
        logger.error(f"Webhook ayarlama hatası: {e}")
        return jsonify(success=False), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Sağlık kontrol endpoint'i"""
    return jsonify(status="OK", message="Bot çalışıyor")

@app.route('/')
def index():
    return "Telegram Müşteri Destek Botu (Gemini 2.5 Flash) Aktif!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
