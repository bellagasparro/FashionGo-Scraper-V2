from flask import Flask, jsonify
import os
import time

app = Flask(__name__)

@app.route('/')
def index():
    return '''
    <h1>🚀 FashionGo Email Scraper - Light</h1>
    <p><strong>Lightweight version for reliable Railway deployment</strong></p>
    <p>✅ Minimal startup footprint</p>
    <p>✅ Deferred heavy imports</p>
    <p>✅ Memory optimized</p>
    <br>
    <a href="/health">Health Check</a> | 
    <a href="/korea-test">Korea Test</a> | 
    <a href="/debug">Debug Info</a>
    '''

@app.route('/health')
def health():
    """Ultra-lightweight health check"""
    return jsonify({
        'status': 'healthy',
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S UTC'),
        'version': '2.0-light',
        'app': 'fashiongo-email-scraper-light'
    }), 200

@app.route('/korea-test')  
def korea_test():
    """Korea connectivity test"""
    from flask import request
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    return jsonify({
        'status': 'accessible_from_korea',
        'user_ip': user_ip,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S UTC'),
        'message': 'Light app is accessible from Korea!'
    })

@app.route('/debug')
def debug():
    """Debug endpoint"""
    import platform
    return jsonify({
        'python_version': platform.python_version(),
        'platform': platform.platform(),
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S UTC'),
        'memory_usage': 'minimal',
        'features': 'lightweight_health_check_only'
    })

@app.route('/upload', methods=['POST'])
def upload_file():
    """Placeholder for email scraping - loads heavy dependencies only when needed"""
    try:
        # Import heavy dependencies only when actually needed
        import pandas as pd
        from flask import request, send_file
        import tempfile
        from werkzeug.utils import secure_filename
        
        return jsonify({
            'success': False, 
            'error': 'Email scraping functionality will be added after successful deployment verification'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Import error: {str(e)}'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) 