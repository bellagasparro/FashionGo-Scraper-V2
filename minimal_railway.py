from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def index():
    return '<h1>FashionGo Email Scraper</h1><p>Working!</p><a href="/health">Health Check</a>'

@app.route('/health')
def health():
    return {'status': 'healthy'}, 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 