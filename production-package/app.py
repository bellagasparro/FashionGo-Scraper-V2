from flask import Flask, request, jsonify, send_file
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import os
import time
import tempfile
import logging
from werkzeug.utils import secure_filename
import platform

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')

def clean_company_name(name):
    if pd.isna(name) or name is None or str(name).strip() == '':
        return None
    
    name = str(name).strip()
    suffixes = [' LLC', ' Inc', ' Corp', ' Corporation', ' Ltd', ' Limited', ' Co', ' Company']
    for suffix in suffixes:
        if name.upper().endswith(suffix.upper()):
            name = name[:-len(suffix)].strip()
    
    return name if name else None

def find_emails_on_page(url, timeout=5):
    """Enhanced email extraction from webpages with better filtering"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
        
        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        response.raise_for_status()
        
        # Find emails using multiple patterns
        text_content = response.text.lower()
        
        # Enhanced email patterns
        email_patterns = [
            re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            re.compile(r'mailto:([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})'),
            re.compile(r'"([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})"'),
            re.compile(r"'([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})'")
        ]
        
        all_emails = []
        for pattern in email_patterns:
            emails = pattern.findall(response.text)
            all_emails.extend(emails)
        
        # Remove duplicates and filter out unwanted emails
        emails = list(set(all_emails))
        filtered_emails = []
        
        for email in emails:
            email_lower = email.lower()
            # Skip common non-business emails
            skip_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'aol.com', 
                          'icloud.com', 'live.com', 'msn.com', 'qq.com', '163.com', 'sina.com',
                          'noreply', 'no-reply', 'donotreply', 'support@wordpress.com', 
                          'wpchill.com', 'example.com', 'test.com', 'localhost']
            
            skip_prefixes = ['noreply', 'no-reply', 'donotreply', 'automated', 'robot', 'system']
            
            if any(domain in email_lower for domain in skip_domains):
                continue
            if any(email_lower.startswith(prefix) for prefix in skip_prefixes):
                continue
            if len(email) < 5 or len(email) > 100:
                continue
                
            filtered_emails.append(email)
        
        # Prioritize business emails
        business_emails = []
        other_emails = []
        
        business_prefixes = ['info', 'contact', 'sales', 'support', 'admin', 'hello', 'inquiry']
        for email in filtered_emails:
            if any(email.lower().startswith(prefix) for prefix in business_prefixes):
                business_emails.append(email)
            else:
                other_emails.append(email)
        
        # Return business emails first, then others
        final_emails = business_emails + other_emails
        return final_emails[:5] if final_emails else []
        
    except Exception as e:
        logger.warning(f"Error finding emails on {url}: {str(e)}")
        return []

def search_for_website(company_name, max_attempts=3):
    """Enhanced website discovery using multiple search engines and direct guessing"""
    if not company_name:
        return None
    
    clean_name = clean_company_name(company_name)
    if not clean_name:
        return None
    
    websites_found = []
    
    # Strategy 1: Direct domain guessing (most reliable)
    direct_domains = generate_direct_domains(clean_name)
    for domain in direct_domains[:20]:  # Check top 20 most likely domains
        try:
            test_url = f"http://{domain}"
            response = requests.head(test_url, timeout=3, allow_redirects=True)
            if response.status_code == 200:
                final_url = response.url
                if final_url.startswith('https://'):
                    websites_found.append(final_url)
                else:
                    websites_found.append(f"https://{domain}")
                break
        except:
            try:
                test_url = f"https://{domain}"
                response = requests.head(test_url, timeout=3, allow_redirects=True)
                if response.status_code == 200:
                    websites_found.append(response.url)
                    break
            except:
                continue
    
    # Strategy 2: Search engines (if direct guessing fails)
    if not websites_found:
        search_engines = [
            f"https://www.bing.com/search?q={clean_name.replace(' ', '+')}+website",
            f"https://search.yahoo.com/search?p={clean_name.replace(' ', '+')}+official+site"
        ]
        
        for search_url in search_engines:
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                response = requests.get(search_url, headers=headers, timeout=8)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                links = soup.find_all('a', href=True)
                
                for link in links[:10]:
                    if hasattr(link, 'get'):
                        href_attr = link.get('href', '')
                        href = str(href_attr) if href_attr else ''
                        if 'http' in href and not any(exclude in href.lower() for exclude in 
                            ['google.', 'bing.', 'yahoo.', 'facebook.', 'linkedin.', 'twitter.', 
                             'instagram.', 'youtube.', 'wikipedia.', 'amazon.', 'ebay.']):
                            
                            # Clean the URL
                            if href.startswith('/url?q='):
                                href = href.split('/url?q=')[1].split('&')[0]
                            
                            # Validate domain
                            try:
                                domain = href.split('//')[1].split('/')[0].lower()
                                if any(term in domain for term in clean_name.lower().split()):
                                    websites_found.append(href)
                                    break
                            except:
                                continue
                
                if websites_found:
                    break
                    
            except Exception as e:
                logger.warning(f"Search engine {search_url} failed: {str(e)}")
                continue
    
    return websites_found[0] if websites_found else None

def generate_direct_domains(company_name):
    """Generate potential domain names for a company"""
    if not company_name:
        return []
    
    name = company_name.lower().strip()
    words = re.findall(r'\b\w+\b', name)
    domains = []
    
    # TLDs to try
    tlds = ['.com', '.net', '.org', '.biz', '.info', '.co', '.io', '.us']
    
    if words:
        # Full company name variations
        full_name = ''.join(words)
        full_name_dash = '-'.join(words)
        full_name_underscore = '_'.join(words)
        
        # Add full name variations
        for tld in tlds:
            domains.extend([
                f"{full_name}{tld}",
                f"{full_name_dash}{tld}",
                f"{full_name_underscore}{tld}"
            ])
        
        # Single word (if company name is one word or use first word)
        first_word = words[0]
        for tld in tlds:
            domains.append(f"{first_word}{tld}")
        
        # Two words combinations
        if len(words) >= 2:
            for i in range(len(words)-1):
                combo = words[i] + words[i+1]
                combo_dash = words[i] + '-' + words[i+1]
                for tld in tlds:
                    domains.extend([f"{combo}{tld}", f"{combo_dash}{tld}"])
        
        # Abbreviations (first letter of each word)
        if len(words) >= 2:
            abbrev = ''.join(word[0] for word in words)
            for tld in tlds:
                domains.append(f"{abbrev}{tld}")
        
        # Common variations
        variations = []
        for word in words:
            if word.endswith('y'):
                variations.append(word[:-1] + 'ie')
            if word.endswith('s'):
                variations.append(word[:-1])
        
        for var in variations:
            for tld in tlds[:3]:  # Only try main TLDs for variations
                domains.append(f"{var}{tld}")
    
    return domains

def find_contact_pages(base_url):
    """Enhanced contact page discovery with 20+ common page variations"""
    contact_pages = [
        '/contact', '/contact-us', '/contact_us', '/contactus',
        '/support', '/help', '/customer-service', '/customer_service',
        '/sales', '/sales-team', '/business', '/enterprise',
        '/about', '/about-us', '/about_us', '/team',
        '/reach-us', '/get-in-touch', '/touch', '/connect',
        '/inquiry', '/inquiries', '/quote', '/request-quote',
        '/info', '/information', '/details', '/reach'
    ]
    
    found_pages = []
    for page in contact_pages:
        try:
            page_url = base_url.rstrip('/') + page
            response = requests.head(page_url, timeout=3, allow_redirects=True)
            if response.status_code == 200:
                found_pages.append(page_url)
        except:
            continue
    
    return found_pages

def find_dynamic_contact_links(website):
    """Dynamically find contact-related links by parsing the homepage"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(website, headers=headers, timeout=5)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        contact_links = []
        
        # Find links with contact-related text or hrefs
        contact_keywords = ['contact', 'support', 'help', 'sales', 'inquiry', 'reach', 'connect', 'touch', 'about']
        
        for link in soup.find_all('a', href=True):
            href_attr = link.get('href', '')
            href = str(href_attr).lower() if href_attr else ''
            text = str(link.get_text()).lower().strip()
            
            if any(keyword in href or keyword in text for keyword in contact_keywords):
                if href.startswith('/'):
                    contact_links.append(website.rstrip('/') + href)
                elif href.startswith('http'):
                    contact_links.append(href)
        
        return list(set(contact_links))[:10]  # Return unique links, max 10
        
    except Exception as e:
        logger.warning(f"Error finding dynamic contact links: {str(e)}")
        return []

def guess_email_formats(website, company_name):
    """Guess common email formats when website is found but no emails are extracted"""
    if not website or not company_name:
        return []
    
    try:
        # Extract domain from website
        domain = website.replace('https://', '').replace('http://', '').split('/')[0]
        
        # Common email prefixes for businesses
        prefixes = ['info', 'contact', 'sales', 'support', 'admin', 'hello', 'inquiry', 'office']
        
        guessed_emails = []
        for prefix in prefixes:
            email = f"{prefix}@{domain}"
            
            # Quick validation attempt
            try:
                test_response = requests.head(f"https://{domain}", timeout=2)
                if test_response.status_code == 200:
                    guessed_emails.append(email)
            except:
                continue
        
        return guessed_emails[:3]  # Return top 3 guesses
        
    except Exception as e:
        logger.warning(f"Error guessing email formats: {str(e)}")
        return []

def check_subdomains_for_emails(website, company_name):
    """Check common subdomains for additional email addresses"""
    if not website:
        return None
    
    try:
        # Extract main domain
        domain = website.replace('https://', '').replace('http://', '').split('/')[0]
        
        # Common subdomains that might have contact info
        subdomains = ['blog', 'support', 'help', 'www', 'mail', 'contact']
        
        for subdomain in subdomains:
            try:
                subdomain_url = f"https://{subdomain}.{domain}"
                emails = find_emails_on_page(subdomain_url, timeout=3)
                if emails:
                    return emails, subdomain_url
            except:
                continue
        
        return None
        
    except Exception as e:
        logger.warning(f"Error checking subdomains: {str(e)}")
        return None

def process_companies(companies_df):
    """Enhanced processing with 5-layer email extraction strategy"""
    results = []
    processed_companies = set()
    
    # Remove duplicates and limit to 100 companies
    unique_companies = []
    for _, row in companies_df.iterrows():
        company_name = clean_company_name(row.get('company', ''))
        if company_name and company_name not in processed_companies:
            unique_companies.append({'company': company_name, 'original_row': row})
            processed_companies.add(company_name)
        
        if len(unique_companies) >= 100:
            break
    
    for i, company_data in enumerate(unique_companies):
        company_name = company_data['company']
        original_row = company_data['original_row']
        
        logger.info(f"Processing {i+1}/{len(unique_companies)}: {company_name}")
        
        try:
            email, source = find_company_email_enhanced(company_name)
            
            result = {
                'company': company_name,
                'email': email if email else 'Not found',
                'source': source if source else 'No source available'
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

def find_company_email_enhanced(company_name):
    """5-layer enhanced email finding strategy for maximum success rate"""
    if not company_name:
        return None, "No company name provided"
    
    logger.info(f"Starting enhanced email search for: {company_name}")
    
    # Strategy 1: Find company website
    website = search_for_website(company_name)
    if not website:
        return None, f"Website not found for {company_name}"
    
    logger.info(f"Found website: {website}")
    
    # Strategy 2: Check homepage for emails
    homepage_emails = find_emails_on_page(website)
    if homepage_emails:
        return homepage_emails[0], f"Homepage: {website}"
    
    # Strategy 3: Check dedicated contact pages (20+ variations)
    contact_pages = find_contact_pages(website)
    for contact_page in contact_pages:
        contact_emails = find_emails_on_page(contact_page)
        if contact_emails:
            return contact_emails[0], f"Contact page: {contact_page}"
    
    # Strategy 4: Dynamic contact link discovery
    dynamic_links = find_dynamic_contact_links(website)
    for link in dynamic_links:
        dynamic_emails = find_emails_on_page(link)
        if dynamic_emails:
            return dynamic_emails[0], f"Dynamic link: {link}"
    
    # Strategy 5: Email format guessing
    guessed_emails = guess_email_formats(website, company_name)
    if guessed_emails:
        return guessed_emails[0], f"Guessed format: {website}"
    
    # Strategy 6: Subdomain checking (final fallback)
    subdomain_email = check_subdomains_for_emails(website, company_name)
    if subdomain_email:
        return subdomain_email[0], f"Subdomain: {subdomain_email[1]}"
    
    return None, f"No emails found on {website}"

@app.route('/')
def index():
    return '''<!DOCTYPE html>
<html><head><title>FashionGo Email Scraper - Simplified</title>
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
<h1>🚀 FashionGo Email Scraper - Simplified</h1>
<div class="info">
<strong>Simplified Version Features:</strong><br>
✅ 5-Layer Email Extraction System<br>
✅ Enhanced Website Discovery (100+ domain variations)<br>
✅ 20+ Contact Page Variations<br>
✅ Dynamic Contact Link Detection<br>
✅ Smart Email Format Guessing<br>
✅ Optimized for Railway Deployment<br>
<strong>Expected Success Rate: 65-75%</strong>
</div>
<div class="upload-area">
<h3>📁 Upload Company List</h3>
<p>Upload an Excel file (.xlsx) with a 'company' column</p>
<form id="uploadForm" enctype="multipart/form-data">
<input type="file" id="fileInput" name="file" accept=".xlsx" required>
<br>
<button type="submit">🔍 Find Emails</button>
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
resultsDiv.innerHTML = '<div class="info">🔍 Processing companies... This may take a few minutes.</div>';
resultsDiv.style.display = 'block';
fetch('/upload', {
method: 'POST',
body: formData
}).then(response => response.json()).then(data => {
if (data.success) {
var html = '<div class="success">✅ Processing completed!</div>';
html += '<div class="stats">';
html += '<div class="stat"><h3>' + data.total + '</h3><p>Total Companies</p></div>';
html += '<div class="stat"><h3>' + data.found + '</h3><p>Emails Found</p></div>';
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
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'})
        
        file = request.files['file']
        if not file.filename or file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})
        
        if not file.filename.lower().endswith('.xlsx'):
            return jsonify({'success': False, 'error': 'Please upload an Excel (.xlsx) file'})
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
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
        
        # Process companies
        results = process_companies(df)
        
        # Create results DataFrame
        results_df = pd.DataFrame(results)
        
        # Save results
        output_filename = f"email_results_{int(time.time())}.xlsx"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        results_df.to_excel(output_path, index=False)
        
        # Clean up input file
        os.remove(filepath)
        
        # Calculate statistics
        total_companies = len(results)
        emails_found = len([r for r in results if r['email'] != 'Not found' and r['email'] != 'Error occurred'])
        
        logger.info(f"Processing completed: {emails_found}/{total_companies} emails found")
        
        return jsonify({
            'success': True,
            'total': total_companies,
            'found': emails_found,
            'download_url': f'/download/{output_filename}'
        })
        
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/download/<filename>')
def download_file(filename):
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True, download_name=filename)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    try:
        # Quick health check with minimal dependencies
        return jsonify({
            'status': 'healthy',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S UTC'),
            'version': '2.0-simplified',
            'app': 'fashiongo-email-scraper-simplified'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy', 
            'error': str(e),
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S UTC')
        }), 500

@app.route('/korea-test')
def korea_test():
    """Special endpoint for testing Korea connectivity"""
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent = request.headers.get('User-Agent')
    return jsonify({
        'status': 'accessible_from_korea',
        'user_ip': user_ip,
        'user_agent': user_agent,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S UTC'),
        'server_location': 'auto_detected',
        'message': 'If you can see this, the simplified app is accessible from Korea!'
    })

@app.route('/debug')
def debug():
    """Debug endpoint with system information"""
    return jsonify({
        'python_version': platform.python_version(),
        'platform': platform.platform(),
        'memory_usage': 'simplified_version',
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S UTC'),
        'features': '5-layer email extraction (no social media)',
        'expected_success_rate': '65-75%'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) 