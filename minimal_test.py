from flask import Flask, jsonify
import os
import time

app = Flask(__name__)

@app.route('/')
def index():
    return '''
    <h1>FashionGo Email Scraper - Minimal Test</h1>
    <p>This is a minimal test version to verify Railway deployment works.</p>
    <p>If you see this, the deployment is successful!</p>
    <a href="/health">Health Check</a>
    '''

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S UTC'),
        'version': 'minimal-test',
        'message': 'Railway deployment successful!'
    }), 200

@app.route('/korea-test')
def korea_test():
    return jsonify({
        'status': 'accessible_from_korea',
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S UTC'),
        'message': 'Minimal app is accessible from Korea!'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) 