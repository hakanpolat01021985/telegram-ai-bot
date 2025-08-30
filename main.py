import os
import logging
from flask import Flask, jsonify

# Flask uygulamasını oluştur
app = Flask(__name__)

# Loglama ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    logger.info("Ana sayfa çağrıldı")
    return jsonify({
        "status": "online", 
        "message": "Flask uygulaması çalışıyor",
        "service": "Telegram Bot Test"
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "port": os.environ.get('PORT', '10000')
    })

@app.route('/test')
def test():
    logger.info("Test endpointi çağrıldı")
    return jsonify({"message": "Test başarılı"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    logger.info(f"Sunucu {port} portunda başlatılıyor...")
    app.run(host='0.0.0.0', port=port, debug=False)
