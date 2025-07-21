import os
import sys
from flask import Flask

print("=== RAILWAY DEBUG START ===")
print(f"Python version: {sys.version}")
print(f"PORT environment variable: {os.environ.get('PORT', 'NOT SET')}")
print(f"Current working directory: {os.getcwd()}")
print(f"Python path: {sys.path}")

app = Flask(__name__)

@app.route('/')
def index():
    return f'''
    <h1>🔍 Railway Debug App</h1>
    <p><strong>Status:</strong> ✅ WORKING!</p>
    <p><strong>Port:</strong> {os.environ.get('PORT', 'NOT SET')}</p>
    <p><strong>Host:</strong> 0.0.0.0</p>
    <p><a href="/health">Health Check →</a></p>
    '''

@app.route('/health')
def health():
    print("Health check called!")
    return {
        'status': 'healthy',
        'port': os.environ.get('PORT', 'NOT SET'),
        'cwd': os.getcwd()
    }, 200

print("=== RAILWAY DEBUG: App routes registered ===")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"=== RAILWAY DEBUG: Starting app on port {port} ===")
    app.run(host='0.0.0.0', port=port, debug=True)
else:
    print("=== RAILWAY DEBUG: App being imported by gunicorn ===") 