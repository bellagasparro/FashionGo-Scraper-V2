print("=== EMAIL SCRAPER DEBUG: Starting imports ===")
from flask import Flask, jsonify
print("✅ Flask imported")
import os
print("✅ os imported")
import time
print("✅ time imported")
import re
print("✅ re imported")

print("=== EMAIL SCRAPER DEBUG: Creating Flask app ===")
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
print("✅ Flask app created")

@app.route('/')
def index():
    return '''<!DOCTYPE html>
<html><head><title>FashionGo Email Scraper - Accurate</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Google+Sans:wght@300;400;500;700&family=Nanum+Myeongjo:wght@400;700&display=swap" rel="stylesheet">
<style>
body { font-family: 'Google Sans', Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: #f6efe2; }
.container { background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); border: 1px solid rgba(246, 239, 226, 0.3); }
h1 { font-family: 'Nanum Myeongjo', serif; color: #2c3e50; text-align: center; margin-bottom: 30px; font-weight: 700; }
.upload-area { border: 2px dashed #3498db; border-radius: 12px; padding: 40px; text-align: center; margin: 20px 0; background: linear-gradient(145deg, #f6efe2, #faf7f2); }
.upload-area:hover { background: linear-gradient(145deg, #f0e6d6, #f6efe2); border-color: #2196f3; }
input[type="file"] { margin: 10px 0; }
button { font-family: 'Google Sans', sans-serif; background: #3498db; color: white; padding: 12px 30px; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; margin: 10px 5px; font-weight: 500; transition: all 0.3s ease; }
button:hover { background: #2980b9; transform: translateY(-1px); box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3); }
.reset-btn { background: #95a5a6; }
.reset-btn:hover { background: #7f8c8d; }
.results { margin-top: 20px; padding: 20px; background: #f8f9fa; border-radius: 5px; }
.error { color: #e74c3c; background: #fdf2f2; padding: 15px; border-radius: 5px; border-left: 4px solid #e74c3c; }
.success { color: #27ae60; background: #f0f9f4; padding: 15px; border-radius: 5px; border-left: 4px solid #27ae60; }
.info { background: #e8f4fd; padding: 15px; border-radius: 5px; margin: 10px 0; border-left: 4px solid #3498db; }
.instructions { background: linear-gradient(145deg, #f0f9f4, #f6efe2); padding: 25px; border-radius: 12px; margin: 20px 0; border-left: 4px solid #27ae60; }
.instructions h3 { font-family: 'Nanum Myeongjo', serif; margin-top: 0; color: #27ae60; font-weight: 700; }
.steps { margin: 15px 0; }
.step { padding: 8px 0; border-bottom: 1px solid #e8f5e8; }
.step:last-child { border-bottom: none; }
.example { background: linear-gradient(145deg, #fff, #f6efe2); padding: 20px; border-radius: 10px; margin-top: 15px; border: 1px solid #d5e8d5; }
.example code { background: #f6efe2; padding: 15px; display: block; border-radius: 8px; font-family: 'Google Sans', monospace; font-size: 14px; line-height: 1.6; border: 1px solid rgba(246, 239, 226, 0.5); }
.warning { background: linear-gradient(145deg, #fff3cd, #f6efe2); padding: 20px; border-radius: 10px; margin-top: 15px; border: 1px solid #ffeaa7; border-left: 4px solid #fdcb6e; }
.warning strong { color: #d63031; }
.stats { display: flex; justify-content: space-around; margin: 20px 0; }
.stat { text-align: center; padding: 15px; background: #fff; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
.stat h3 { margin: 0; color: #2c3e50; }
.stat p { margin: 5px 0 0 0; color: #7f8c8d; }
</style></head><body>
<div class="container">
<h1>🚀 FashionGo Email Scraper</h1>
<div class="info">
<strong>📧 Overview:</strong> Accurate email extraction system that finds real business contact emails with high quality results.<br>
<strong>⚡ Capacity:</strong> Process up to 300 companies in 2-5 minutes depending on file size.
</div>
<div class="instructions">
<h3>📋 Quick Setup Instructions</h3>
<div class="steps">
<div class="step">
<strong>Step 1:</strong> Prepare your file in <strong>CSV (.csv)</strong> or <strong>Excel (.xlsx)</strong> format
</div>
<div class="step">
<strong>Step 2:</strong> Ensure you have a column named exactly <strong>'company'</strong> (lowercase)
</div>
<div class="step">
<strong>Step 3:</strong> Keep file size under <strong>16MB</strong> (up to 300 companies recommended)
</div>
<div class="step">
<strong>Step 4:</strong> Upload and let us find the emails automatically!
</div>
</div>
<div class="example">
<strong>📄 Example file structure:</strong><br>
<code>
company,industry<br>
Nike,Sportswear<br>
Zara,Fashion<br>
H&M,Retail
</code>
</div>
</div>
<div class="upload-area">
<h3>📁 Upload Company List</h3>
<p>Ready? Upload your file below:</p>
<form id="uploadForm" enctype="multipart/form-data">
<input type="file" id="fileInput" name="file" accept=".csv,.xlsx" required>
<br>
<button type="submit">🔍 Find Real Emails</button>
<button type="button" class="reset-btn" onclick="resetForm()">🔄 Reset</button>
</form>
</div>
<div class="warning">
<strong>⚠️ Common Issues:</strong><br>
• Column named "Company" (uppercase) → Change to "company" (lowercase)<br>
• Column named "business_name" → Change to "company"<br>
• File over 16MB → Split into smaller files<br>
• Wrong format (.txt, .doc) → Convert to .csv or .xlsx
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
        
        if not file.filename.lower().endswith(('.csv', '.xlsx')):
            return jsonify({'success': False, 'error': 'Please upload a CSV (.csv) or Excel (.xlsx) file'})
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(tempfile.gettempdir(), filename)
        file.save(filepath)
        
        # Read the CSV or Excel file
        try:
            if filepath.lower().endswith('.csv'):
                df = pd.read_csv(filepath)
            elif filepath.lower().endswith('.xlsx'):
                df = pd.read_excel(filepath)
            else:
                os.remove(filepath)
                return jsonify({'success': False, 'error': 'Unsupported file format'})
        except Exception as e:
            os.remove(filepath)
            return jsonify({'success': False, 'error': f'Error reading file: {str(e)}'})
        
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
    start_time = time.time()
    
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
        # Timeout check - stop after 8 minutes to prevent long hangs
        if time.time() - start_time > 480:  # 8 minutes
            logger.warning(f"Processing timeout reached at company {i+1}, stopping...")
            break
            
        company_name = company_data['company']
        original_row = company_data['original_row']
        
        logger.info(f"Processing {i+1}/{len(unique_companies)}: {company_name}")
        
        try:
            email, source = find_real_email_only(company_name, requests)
            
            result = {
                'company': company_name,
                'email': email if email else '',  # Empty instead of 'Not found'
                'source': source if source else 'No emails found'
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
            # Add any additional columns from original data even on error
            try:
                for col in original_row.index:
                    if col.lower() not in ['company']:
                        result[col] = original_row[col]
            except:
                pass
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

def search_engines_fallback(company_name, requests):
    """Search Bing and Yahoo when direct domain guessing fails"""
    try:
        search_engines = [
            f"https://www.bing.com/search?q=\"{company_name}\"+website",
            f"https://search.yahoo.com/search?p=\"{company_name}\"+official+site"
        ]
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        for search_url in search_engines:
            try:
                response = requests.get(search_url, headers=headers, timeout=5)
                if response.status_code == 200:
                    content = response.text.lower()
                    
                    # Simple extraction of URLs from search results
                    import re
                    url_pattern = re.compile(r'https?://(?:www\.)?([a-zA-Z0-9.-]+\.com)[^"\s]*')
                    matches = url_pattern.findall(content)
                    
                    # Filter for likely company websites
                    for domain in matches[:10]:
                        if any(word in domain.lower() for word in company_name.lower().split() if len(word) > 3):
                            try:
                                test_url = f"https://www.{domain}"
                                test_response = requests.head(test_url, timeout=3, allow_redirects=True)
                                if test_response.status_code == 200:
                                    return test_url
                            except:
                                try:
                                    test_url = f"https://{domain}"
                                    test_response = requests.head(test_url, timeout=3, allow_redirects=True)
                                    if test_response.status_code == 200:
                                        return test_url
                                except:
                                    continue
                
                time.sleep(0.5)  # Rate limiting between search engines
            except:
                continue
                
        return None
    except:
        return None

def guess_common_email_formats(website):
    """Guess common email formats when website found but no emails extracted"""
    try:
        # Extract domain from website
        domain = website.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0]
        
        # Common business email prefixes (ordered by likelihood)
        prefixes = ['info', 'contact', 'sales', 'support', 'hello', 'inquiry', 'admin', 'office']
        
        for prefix in prefixes:
            # Return first format - most likely to be real
            return f"{prefix}@{domain}"
            
        return None
    except:
        return None

def find_dynamic_contact_links(website, requests):
    """Find contact links by parsing the homepage"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(website, headers=headers, timeout=3)
        response.raise_for_status()
        
        # Simple text-based link finding using basic string search
        content = response.text.lower()
        contact_links = []
        
        # Look for simple href patterns with contact keywords
        contact_keywords = ['contact', 'about', 'support', 'help', 'sales']
        
        for keyword in contact_keywords:
            # Simple search for href="/keyword" or href="/page-with-keyword"
            if f'href="/{keyword}"' in content:
                contact_links.append(f"{website.rstrip('/')}/{keyword}")
            elif f"href='/{keyword}'" in content:
                contact_links.append(f"{website.rstrip('/')}/{keyword}")
            # Also check for href="/keyword-us" etc.
            if f'href="/{keyword}-' in content:
                start_idx = content.find(f'href="/{keyword}-')
                if start_idx != -1:
                    end_idx = content.find('"', start_idx + 6)
                    if end_idx != -1:
                        link_path = content[start_idx + 6:end_idx]
                        contact_links.append(f"{website.rstrip('/')}{link_path}")
        
        return list(set(contact_links[:5]))  # Remove duplicates, limit to 5
    except:
        return []

def check_instagram_email(company_name, requests):
    """Check Instagram profile for publicly available contact emails (fashion industry focused)"""
    try:
        if not company_name:
            return None
            
        clean_name = clean_company_name(company_name)
        if not clean_name:
            return None
        
        # Quick timeout to prevent hanging (max 8 seconds per company for Instagram)
        start_time = time.time()
            
        # Create potential Instagram usernames for fashion companies (limited for speed)
        potential_usernames = [
            clean_name.lower().replace(' ', ''),
            clean_name.lower().replace(' ', '_'),
        ]
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
        
        # Check each potential username (with timeout protection)
        for username in potential_usernames:
            # Stop if taking too long
            if time.time() - start_time > 8:
                break
                
            try:
                # Use Instagram's public profile endpoint (no login required)
                instagram_url = f"https://www.instagram.com/{username}/"
                
                response = requests.get(instagram_url, headers=headers, timeout=3)
                if response.status_code == 200:
                    # Look for emails in the publicly visible content
                    page_content = response.text.lower()
                    
                    # Instagram-specific email patterns (from bio/contact info)
                    email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', re.IGNORECASE)
                    emails = email_pattern.findall(page_content)
                    
                    if emails:
                        # Filter out generic emails
                        business_emails = []
                        skip_patterns = ['instagram.com', 'facebook.com', 'gmail.com', 'yahoo.com', 'hotmail.com']
                        
                        for email in emails:
                            email_lower = email.lower()
                            if not any(skip in email_lower for skip in skip_patterns):
                                business_emails.append(email)
                        
                        if business_emails:
                            return business_emails[0], instagram_url
                
                # Quick rate limiting
                time.sleep(0.3)
                
            except Exception as e:
                # Continue to next username if this one fails
                continue
        
        return None
        
    except Exception as e:
        # Don't let Instagram errors break the main flow
        return None

def find_real_email_only(company_name, requests):
    """Find REAL emails only - no guessing, high accuracy"""
    if not company_name:
        return None, "No company name provided"
    
    clean_name = clean_company_name(company_name)
    if not clean_name:
        return None, "Invalid company name"
    
    # Try comprehensive domain patterns for better website discovery
    domains_to_try = [
        f"{clean_name.lower().replace(' ', '')}.com",
        f"{clean_name.lower().replace(' ', '-')}.com",
        f"{clean_name.lower().replace(' ', '_')}.com",
        f"{clean_name.lower().replace(' ', '')}.net",
        f"{clean_name.lower().replace(' ', '')}.org",
        f"{clean_name.lower().replace(' ', '')}.co",
        f"{clean_name.lower().replace(' ', '')}.io",
        f"{clean_name.lower().split()[0]}.com" if ' ' in clean_name else None,
        f"{''.join([word[0] for word in clean_name.lower().split()])}.com" if ' ' in clean_name else None
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
                
                # Check comprehensive contact pages (20+ variations)
                contact_pages = [
                    '/contact', '/contact-us', '/contact_us', '/contactus',
                    '/about', '/about-us', '/about_us', '/team',
                    '/support', '/help', '/customer-service', '/customer_service',
                    '/sales', '/sales-team', '/business', '/enterprise',
                    '/reach-us', '/get-in-touch', '/touch', '/connect',
                    '/inquiry', '/inquiries', '/info', '/information'
                ]
                
                for page in contact_pages:
                    try:
                        contact_url = f"{website}{page}"
                        contact_email = extract_real_emails(contact_url, requests)
                        if contact_email:
                            return contact_email, f"Contact page: {contact_url}"
                        time.sleep(0.1)  # Quick rate limiting
                    except:
                        continue
                
                # Dynamic contact link discovery
                try:
                    dynamic_links = find_dynamic_contact_links(website, requests)
                    for link in dynamic_links[:5]:  # Check top 5 dynamic links
                        try:
                            dynamic_email = extract_real_emails(link, requests)
                            if dynamic_email:
                                return dynamic_email, f"Dynamic link: {link}"
                            time.sleep(0.1)
                        except:
                            continue
                except:
                    pass
                
                # No email guessing - only real extracted emails for accuracy
                
                # Website found but no emails - return this info
                return None, f"Website found ({website}) but no emails detected"
        except:
            continue
    
    # No search engine fallback - too inaccurate, returns random websites
    
    # Final fallback: Check Instagram for publicly available contact info
    instagram_email = check_instagram_email(company_name, requests)
    if instagram_email:
        return instagram_email[0], f"Instagram profile: {instagram_email[1]}"
    
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
        
        # Filter out common non-business emails and obviously fake ones
        business_emails = []
        skip_patterns = [
            'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'aol.com',
            'noreply', 'no-reply', 'donotreply', 'mailer-daemon', 'postmaster',
            'wordpress.com', 'example.com', 'test.com', 'localhost',
            'cognitive.ai', 'openai.com', 'ai.com', 'tech.com',  # Filter AI/tech domains
            'admin@admin', 'test@test', 'user@user', '@a.com', '@b.com'  # Filter fake patterns
        ]
        
        for email in emails:
            email_lower = email.lower()
            # More strict validation - email must look legitimate
            if (not any(skip in email_lower for skip in skip_patterns) and 
                len(email) > 5 and 
                '@' in email and 
                '.' in email.split('@')[1] and
                not email.startswith('@') and
                not email.endswith('@')):
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
    print("🩺 Health check called!")
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

print("=== EMAIL SCRAPER DEBUG: Routes registered ===")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"=== EMAIL SCRAPER DEBUG: Starting Flask app on port {port} ===")
    app.run(host='0.0.0.0', port=port, debug=False) 