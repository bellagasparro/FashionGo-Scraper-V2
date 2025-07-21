from flask import Flask, jsonify
import os
import time
import re

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

@app.route('/')
def index():
    return '''<!DOCTYPE html>
<html><head><title>FashionGo Email Scraper - Accurate</title>
<style>
body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
.container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
h1 { color: #2c3e50; text-align: center; margin-bottom: 30px; }
.upload-area { border: 2px dashed #3498db; border-radius: 10px; padding: 40px; text-align: center; margin: 20px 0; background: #f8f9fa; }
.upload-area:hover { background: #e3f2fd; border-color: #2196f3; }
input[type="file"] { margin: 10px 0; }
button { background: #3498db; color: white; padding: 12px 30px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; margin: 10px 5px; }
button:hover { background: #2980b9; }
.reset-btn { background: #95a5a6; }
.reset-btn:hover { background: #7f8c8d; }
.results { margin-top: 20px; padding: 20px; background: #f8f9fa; border-radius: 5px; }
.error { color: #e74c3c; background: #fdf2f2; padding: 15px; border-radius: 5px; border-left: 4px solid #e74c3c; }
.success { color: #27ae60; background: #f0f9f4; padding: 15px; border-radius: 5px; border-left: 4px solid #27ae60; }
.info { background: #e8f4fd; padding: 15px; border-radius: 5px; margin: 10px 0; border-left: 4px solid #3498db; }
.stats { display: flex; justify-content: space-around; margin: 20px 0; }
.stat { text-align: center; padding: 15px; background: #fff; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
.stat h3 { margin: 0; color: #2c3e50; }
.stat p { margin: 5px 0 0 0; color: #7f8c8d; }
</style></head><body>
<div class="container">
<h1>🚀 FashionGo Email Scraper</h1>
<div class="info">
<strong>Accurate Email Extraction:</strong><br>
✅ Real emails only (no guessing)<br>
✅ Website discovery + contact page scanning<br>
✅ Business email prioritization<br>
✅ Processes up to <strong>300 companies</strong> per batch<br>
<strong>Expected Success Rate: 50-65% (high accuracy)</strong><br>
<strong>Processing Time: 2-3 min (100 companies), 8-10 min (300 companies)</strong>
</div>
<div class="upload-area">
<h3>📁 Upload Company List</h3>
<p>Upload an Excel file (.xlsx) with a 'company' column</p>
<form id="uploadForm" enctype="multipart/form-data">
<input type="file" id="fileInput" name="file" accept=".xlsx" required>
<br>
<button type="submit">🔍 Find Real Emails</button>
<button type="button" class="reset-btn" onclick="resetForm()">🔄 Reset</button>
</form>
</div>
<div id="results" style="display:none;"></div>
<div id="error" style="display:none;"></div>
</div>
<script>
document.getElementById('uploadForm').onsubmit = function(e) {
e.preventDefault();
var formData = new FormData();
var fileInput = document.getElementById('fileInput');
if (!fileInput.files[0]) {
alert('Please select a file first!');
return;
}
formData.append('file', fileInput.files[0]);
document.getElementById('results').style.display = 'none';
document.getElementById('error').style.display = 'none';
var resultsDiv = document.getElementById('results');
resultsDiv.innerHTML = '<div class="info">🔍 Finding real emails... This may take several minutes.</div>';
resultsDiv.style.display = 'block';
fetch('/upload', {
method: 'POST',
body: formData
}).then(response => response.json()).then(data => {
if (data.success) {
var html = '<div class="success">✅ Processing completed!</div>';
html += '<div class="stats">';
html += '<div class="stat"><h3>' + data.total + '</h3><p>Total Companies</p></div>';
html += '<div class="stat"><h3>' + data.found + '</h3><p>Real Emails Found</p></div>';
html += '<div class="stat"><h3>' + Math.round((data.found/data.total)*100) + '%</h3><p>Success Rate</p></div>';
html += '</div>';
html += '<button onclick="downloadResults()">📥 Download Results</button>';
document.getElementById('results').innerHTML = html;
window.downloadUrl = data.download_url;
} else {
document.getElementById('error').innerHTML = '<div class="error">❌ Error: ' + data.error + '</div>';
document.getElementById('error').style.display = 'block';
document.getElementById('results').style.display = 'none';
}
}).catch(error => {
document.getElementById('error').innerHTML = '<div class="error">❌ Network error: ' + error.message + '</div>';
document.getElementById('error').style.display = 'block';
document.getElementById('results').style.display = 'none';
});
};
function downloadResults(){
if(window.downloadUrl){
window.location.href = window.downloadUrl;
}}
function resetForm(){document.getElementById('results').style.display='none';
document.getElementById('error').style.display='none';document.getElementById('fileInput').value='';}
</script></body></html>'''

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        # Import heavy dependencies only when needed
        import pandas as pd
        from flask import request, send_file
        import tempfile
        from werkzeug.utils import secure_filename
        import logging
        import requests
        
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'})
        
        file = request.files['file']
        if not file.filename or file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})
        
        if not file.filename.lower().endswith('.xlsx'):
            return jsonify({'success': False, 'error': 'Please upload an Excel (.xlsx) file'})
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(tempfile.gettempdir(), filename)
        file.save(filepath)
        
        # Read the Excel file
        try:
            df = pd.read_excel(filepath)
        except Exception as e:
            os.remove(filepath)
            return jsonify({'success': False, 'error': f'Error reading Excel file: {str(e)}'})
        
        # Check if 'company' column exists
        if 'company' not in df.columns:
            available_columns = ', '.join(df.columns.tolist())
            os.remove(filepath)
            return jsonify({'success': False, 'error': f'No "company" column found. Available columns: {available_columns}'})
        
        # Process companies - accurate emails only
        results = process_companies_accurate(df, logger, requests)
        
        # Create results DataFrame
        results_df = pd.DataFrame(results)
        
        # Save results
        output_filename = f"email_results_{int(time.time())}.xlsx"
        output_path = os.path.join(tempfile.gettempdir(), output_filename)
        results_df.to_excel(output_path, index=False)
        
        # Clean up input file
        os.remove(filepath)
        
        # Calculate statistics
        total_companies = len(results)
        emails_found = len([r for r in results if r['email'] != 'Not found' and r['email'] != 'Error occurred'])
        
        logger.info(f"Processing completed: {emails_found}/{total_companies} real emails found")
        
        return jsonify({
            'success': True,
            'total': total_companies,
            'found': emails_found,
            'download_url': f'/download/{output_filename}'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/download/<filename>')
def download_file(filename):
    try:
        from flask import send_file
        from werkzeug.utils import secure_filename
        import tempfile
        
        filepath = os.path.join(tempfile.gettempdir(), secure_filename(filename))
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True, download_name=filename)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def process_companies_accurate(companies_df, logger, requests):
    """Accurate processing - real emails only, no guessing"""
    results = []
    processed_companies = set()
    
    # Remove duplicates and limit to 300 companies
    unique_companies = []
    for _, row in companies_df.iterrows():
        company_name = clean_company_name(row.get('company', ''))
        if company_name and company_name not in processed_companies:
            unique_companies.append({'company': company_name, 'original_row': row})
            processed_companies.add(company_name)
        
        if len(unique_companies) >= 300:
            break
    
    for i, company_data in enumerate(unique_companies):
        company_name = company_data['company']
        original_row = company_data['original_row']
        
        logger.info(f"Processing {i+1}/{len(unique_companies)}: {company_name}")
        
        try:
            email, source = find_real_email_only(company_name, requests)
            
            result = {
                'company': company_name,
                'email': email if email else 'Not found',
                'source': source if source else 'No emails found on website'
            }
            
            # Add any additional columns from original data
            for col in original_row.index:
                if col.lower() not in ['company']:
                    result[col] = original_row[col]
            
            results.append(result)
            
        except Exception as e:
            logger.error(f"Error processing {company_name}: {str(e)}")
            result = {
                'company': company_name,
                'email': 'Error occurred',
                'source': f'Error: {str(e)}'
            }
            results.append(result)
        
        # Delay to avoid overwhelming servers
        time.sleep(0.5)
    
    return results

def clean_company_name(name):
    if not name or str(name).strip() == '':
        return None
    
    name = str(name).strip()
    suffixes = [' LLC', ' Inc', ' Corp', ' Corporation', ' Ltd', ' Limited', ' Co', ' Company']
    for suffix in suffixes:
        if name.upper().endswith(suffix.upper()):
            name = name[:-len(suffix)].strip()
    
    return name if name else None

def find_real_email_only(company_name, requests):
    """Find REAL emails only - no guessing, high accuracy"""
    if not company_name:
        return None, "No company name provided"
    
    clean_name = clean_company_name(company_name)
    if not clean_name:
        return None, "Invalid company name"
    
    # Try common domain patterns to find actual websites
    domains_to_try = [
        f"{clean_name.lower().replace(' ', '')}.com",
        f"{clean_name.lower().replace(' ', '-')}.com",
        f"{clean_name.lower().replace(' ', '')}.net",
        f"{clean_name.lower().split()[0]}.com" if ' ' in clean_name else None
    ]
    
    # Remove None values
    domains_to_try = [d for d in domains_to_try if d]
    
    for domain in domains_to_try:
        try:
            website = f"https://{domain}"
            response = requests.head(website, timeout=3, allow_redirects=True)
            if response.status_code == 200:
                # Website found - now look for REAL emails only
                
                # Check homepage
                email = extract_real_emails(website, requests)
                if email:
                    return email, f"Homepage: {website}"
                
                # Check contact page
                contact_url = f"{website}/contact"
                contact_email = extract_real_emails(contact_url, requests)
                if contact_email:
                    return contact_email, f"Contact page: {contact_url}"
                
                # Check about page
                about_url = f"{website}/about"
                about_email = extract_real_emails(about_url, requests)
                if about_email:
                    return about_email, f"About page: {about_url}"
                
                # Website found but no emails - return this info
                return None, f"Website found ({website}) but no emails detected"
        except:
            continue
    
    return None, f"No website found for {company_name}"

def extract_real_emails(url, requests):
    """Extract real emails from webpage - no guessing"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        
        # Email regex pattern
        email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        emails = email_pattern.findall(response.text)
        
        if not emails:
            return None
        
        # Filter out common non-business emails
        business_emails = []
        skip_patterns = [
            'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'aol.com',
            'noreply', 'no-reply', 'donotreply', 'mailer-daemon', 'postmaster',
            'wordpress.com', 'example.com', 'test.com', 'localhost'
        ]
        
        for email in emails:
            email_lower = email.lower()
            if not any(skip in email_lower for skip in skip_patterns):
                business_emails.append(email)
        
        if not business_emails:
            return None
        
        # Prioritize business-looking emails
        priority_prefixes = ['info', 'contact', 'sales', 'support', 'admin', 'hello']
        priority_emails = []
        other_emails = []
        
        for email in business_emails:
            if any(email.lower().startswith(prefix) for prefix in priority_prefixes):
                priority_emails.append(email)
            else:
                other_emails.append(email)
        
        # Return best email found
        if priority_emails:
            return priority_emails[0]
        elif other_emails:
            return other_emails[0]
        
        return None
        
    except:
        return None

@app.route('/health')
def health():
    """Ultra-fast health check"""
    return jsonify({
        'status': 'healthy',
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S UTC'),
        'version': '2.0-accurate',
        'app': 'fashiongo-email-scraper-accurate'
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
        'message': 'Accurate app is accessible from Korea!'
    })

@app.route('/debug')
def debug():
    """Debug endpoint"""
    import platform
    return jsonify({
        'python_version': platform.python_version(),
        'platform': platform.platform(),
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S UTC'),
        'memory_usage': 'minimal_startup',
        'features': 'real emails only - no guessing'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) 