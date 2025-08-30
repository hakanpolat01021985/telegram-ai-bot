import os
import logging
from flask import Flask, jsonify, request
import google.generativeai as genai

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

logger.info(f"TELEGRAM_TOKEN: {'***' if TELEGRAM_TOKEN else 'MISSING'}")
logger.info(f"GEMINI_API_KEY: {'***' if GEMINI_API_KEY else 'MISSING'}")

# Gemini setup
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        logger.info("Gemini başarıyla yapılandırıldı")
    except Exception as e:
        logger.error(f"Gemini hatası: {e}")
        model = None
else:
    model = None
    logger.warning("GEMINI_API_KEY bulunamadı")

@app.route('/')
def index():
    return jsonify({
        "status": "online",
        "telegram_configured": bool(TELEGRAM_TOKEN),
        "gemini_configured": model is not None
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        logger.info(f"Webhook data: {data}")
        
        # Basit bir yanıt
        return jsonify({
            "status": "success",
            "message": "Webhook received",
            "telegram_configured": bool(TELEGRAM_TOKEN)
        })
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/test-gemini')
def test_gemini():
    if not model:
        return jsonify({"error": "Gemini not configured"}), 400
    
    try:
        response = model.generate_content("Merhaba, çalışıyor musun?")
        return jsonify({
            "success": True,
            "response": response.text
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    logger.info(f"Sunucu {port} portunda başlatılıyor")
    app.run(host='0.0.0.0', port=port, debug=False)
