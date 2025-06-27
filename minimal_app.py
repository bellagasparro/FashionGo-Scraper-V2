from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <html>
    <head><title>FashionGo Email Finder - Test</title></head>
    <body style="font-family: Arial; padding: 20px; background: #f0f0f0;">
        <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <h1 style="color: #2c5aa0;">🎉 FashionGo Email Finder</h1>
            <p><strong>Status:</strong> ✅ App is running successfully!</p>
            <p><strong>Next step:</strong> Upload functionality will be added once basic deployment works.</p>
            <div style="background: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3>🔧 Debug Info:</h3>
                <p><strong>Python version:</strong> Working</p>
                <p><strong>Flask:</strong> Running</p>
                <p><strong>Port:</strong> ''' + str(os.environ.get('PORT', 5000)) + '''</p>
                <p><strong>Environment:</strong> Production</p>
            </div>
            <p style="color: #666; font-size: 14px;">If you can see this page, the basic Flask app is working correctly!</p>
        </div>
    </body>
    </html>
    '''

@app.route('/health')
def health():
    return {'status': 'healthy', 'message': 'Minimal app running'}, 200

@app.route('/test')
def test():
    return {'test': 'success', 'port': os.environ.get('PORT', 5000)}, 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting app on port {port}")
    app.run(debug=False, host='0.0.0.0', port=port) 