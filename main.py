import os
import logging
from flask import Flask, request, jsonify
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

# Hata ayıklama için değişkenleri logla
logger.info(f"TELEGRAM_TOKEN: {'***' if TELEGRAM_TOKEN else 'MISSING'}")
logger.info(f"GEMINI_API_KEY: {'***' if GEMINI_API_KEY else 'MISSING'}")
logger.info(f"WEBHOOK_URL: {WEBHOOK_URL or 'MISSING'}")

# Gemini AI yapılandırması
try:
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        logger.info("Gemini AI başarıyla yapılandırıldı")
    else:
        model = None
        logger.warning("GEMINI_API_KEY bulunamadı, Gemini devre dışı")
except Exception as e:
    logger.error(f"Gemini AI yapılandırma hatası: {e}")
    model = None

@app.route('/')
def index():
    return jsonify({
        "status": "online",
        "service": "Telegram Support Bot",
        "gemini_configured": model is not None
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "telegram_token_configured": bool(TELEGRAM_TOKEN),
        "gemini_configured": model is not None,
        "webhook_url": WEBHOOK_URL or "Not configured"
    })

@app.route('/test-gemini')
def test_gemini():
    if not model:
        return jsonify({"error": "Gemini not configured"}), 500
    
    try:
        response = model.generate_content("Merhaba, nasılsın?")
        return jsonify({
            "success": True,
            "response": response.text
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/webhook', methods=['POST'])
def webhook():
    # Basit webhook endpoint - daha sonra Telegram entegrasyonu eklenecek
    return jsonify({"status": "webhook_received"})

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    # Basit webhook ayarlama - daha sonra Telegram entegrasyonu eklenecek
    return jsonify({
        "status": "webhook_set",
        "url": f"{WEBHOOK_URL}/webhook" if WEBHOOK_URL else "Not configured"
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
