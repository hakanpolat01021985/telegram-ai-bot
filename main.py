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
WEBHOOK_URL = os.environ.get('RENDER_EXTERNAL_URL') or os.environ.get('WEBHOOK_URL')

# Hata ayıklama için değişkenleri logla
logger.info("Uygulama başlatılıyor...")
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
        "service": "Telegram Support Bot with Gemini",
        "gemini_configured": model is not None,
        "environment": "production"
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
        response = model.generate_content("Merhaba, nasılsın? Kendini kısaca tanıtır mısın?")
        return jsonify({
            "success": True,
            "response": response.text[:500] + "..." if len(response.text) > 500 else response.text
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        logger.info(f"Webhook received: {data}")
        return jsonify({"status": "success", "message": "Webhook received"})
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/set-webhook', methods=['GET', 'POST'])
def set_webhook():
    if not WEBHOOK_URL:
        return jsonify({"status": "error", "message": "WEBHOOK_URL not configured"}), 500
    
    webhook_url = f"{WEBHOOK_URL}/webhook"
    return jsonify({
        "status": "success",
        "message": "Webhook URL generated",
        "webhook_url": webhook_url,
        "instructions": "Set this URL in your Telegram bot settings"
    })

if __name__ == '__main__':
    # Production için Gunicorn kullanılacak, bu kısım sadece development için
    port = int(os.environ.get('PORT', 10000))
    logger.info(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
