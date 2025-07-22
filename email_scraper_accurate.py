print("=== EMAIL SCRAPER DEBUG: Starting imports ===")
from flask import Flask, jsonify, request, send_file, render_template_string
print("✅ Flask imported")
import os
print("✅ os imported")
import time
print("✅ time imported")
import re
print("✅ re imported")
import tempfile
import pandas as pd
import logging
import openai

print("=== EMAIL SCRAPER DEBUG: Creating Flask app ===")
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
print("✅ Flask app created")

# Set up OpenAI API key (you'll need to add this to your environment variables)
openai.api_key = os.getenv('OPENAI_API_KEY')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
<strong>�� Overview:</strong> Simple, proven email extraction like last week that gave ~30% success rate. Clean domain generation + 3 key pages per site. Fast and reliable.<br>
<strong>⚡ Capacity:</strong> Process up to 200 companies in ~3-5 minutes. Each company takes 2-4 seconds with simple, effective extraction.
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
company,phoneNumber,billingCity,billingState,billingCountry<br>
Nike,503-555-0123,Beaverton,OR,USA<br>
Zara,212-555-0456,New York,NY,USA<br>
H&M,+46-8-555-0789,Stockholm,,Sweden<br>
Target,612-555-0789,Minneapolis,MN,USA
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
}).then(response => {
if (!response.ok) {
throw new Error(`Server error: ${response.status} ${response.statusText}`);
}
return response.json();
}).then(data => {
// Validate that data exists and has expected structure
if (!data) {
throw new Error('Empty response from server');
}

if (data.success) {
var html = '<div class="success">✅ Processing completed!</div>';
html += '<div class="stats">';
html += '<div class="stat"><h3>' + (data.total || 0) + '</h3><p>Total Companies</p></div>';
html += '<div class="stat"><h3>' + (data.found || 0) + '</h3><p>Real Emails Found</p></div>';
html += '<div class="stat"><h3>' + (data.total > 0 ? Math.round(((data.found || 0)/(data.total || 1))*100) : 0) + '%</h3><p>Success Rate</p></div>';
html += '</div>';
html += '<button onclick="downloadResults()">📥 Download Results</button>';
document.getElementById('results').innerHTML = html;
window.downloadUrl = data.download_url;
} else {
var errorMsg = data.error || 'Unknown server error occurred';
document.getElementById('error').innerHTML = '<div class="error">❌ Error: ' + errorMsg + '</div>';
document.getElementById('error').style.display = 'block';
document.getElementById('results').style.display = 'none';
}
}).catch(error => {
var errorMessage = 'Network error: ' + (error.message || error.toString());
document.getElementById('error').innerHTML = '<div class="error">❌ ' + errorMessage + '</div>';
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
        from werkzeug.utils import secure_filename
        import requests
        
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'})
        
        file = request.files['file']
        if not file.filename or file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})
        
        if not file.filename.lower().endswith(('.csv', '.xlsx')):
            return jsonify({'success': False, 'error': 'Please upload a CSV (.csv) or Excel (.xlsx) file'})
        
        # Save uploaded file with unique name to avoid conflicts
        file_ext = '.xlsx' if file.filename.lower().endswith('.xlsx') else '.csv'
        unique_filename = f"upload_{int(time.time())}_{file.filename}"
        filepath = os.path.join(tempfile.gettempdir(), secure_filename(unique_filename))
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
        
        # Check for company column (flexible matching)
        company_column = None
        potential_company_columns = [
            'company', 'Company', 'COMPANY', 
            'companyName', 'company_name', 'Company Name', 'Company_Name',
            'shipToCompanyName', 'ship_to_company_name', 'Ship To Company Name',
            'business_name', 'Business Name', 'BusinessName',
            'organization', 'Organization', 'org_name',
            'client', 'Client', 'customer', 'Customer'
        ]
        
        for col in potential_company_columns:
            if col in df.columns:
                company_column = col
                break
        
        if not company_column:
            available_columns = ', '.join(df.columns.tolist())
            os.remove(filepath)
            return jsonify({'success': False, 'error': f'No company column found. Available columns: {available_columns}. Please ensure one column contains company names.'})
        
        logger.info(f"Using company column: {company_column}")
        
        # Rename the company column to 'company' for consistent processing
        df = df.rename(columns={company_column: 'company'})
        
        # Process companies - accurate emails only
        try:
            logger.info("Starting process_companies_simple...")
            results = process_companies_simple(df, logger)
            logger.info(f"process_companies_simple completed with {len(results) if results else 0} results")
        except Exception as process_error:
            logger.error(f"Error in process_companies_simple: {type(process_error).__name__}: {str(process_error)}")
            raise Exception(f"Processing failed: {str(process_error)}")
        
        # Validate results before DataFrame creation
        if not results:
            logger.error("No results returned from processing")
            return jsonify({'success': False, 'error': 'No results generated during processing'})
        
        # Create results DataFrame with better error handling
        try:
            logger.info(f"Creating DataFrame from {len(results)} results...")
            # Log the structure of first result for debugging
            if results:
                first_result = results[0]
                logger.info(f"First result structure: {list(first_result.keys()) if hasattr(first_result, 'keys') else type(first_result)}")
            
            results_df = pd.DataFrame(results)
            logger.info(f"DataFrame created successfully with shape: {results_df.shape}")
        except Exception as df_error:
            logger.error(f"Error creating DataFrame: {type(df_error).__name__}: {str(df_error)}")
            # Try to provide more debug info
            logger.error(f"Results type: {type(results)}, Length: {len(results) if hasattr(results, '__len__') else 'unknown'}")
            if results and len(results) > 0:
                logger.error(f"First result: {results[0]}")
            raise Exception(f"DataFrame creation failed: {str(df_error)}")
        
        # Save results with unique filename
        try:
            timestamp = int(time.time())
            output_filename = f"email_results_{timestamp}.xlsx"
            output_path = os.path.join(tempfile.gettempdir(), output_filename)
            logger.info(f"Saving results to: {output_path}")
            results_df.to_excel(output_path, index=False)
            logger.info("Excel file saved successfully")
        except Exception as save_error:
            logger.error(f"Error saving Excel file: {type(save_error).__name__}: {str(save_error)}")
            raise Exception(f"File save failed: {str(save_error)}")
        
        # Clean up input file
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info("Input file cleaned up")
        except Exception as cleanup_error:
            logger.warning(f"Could not clean up input file: {str(cleanup_error)}")
        
        # Calculate statistics with error handling
        try:
            total_companies = len(results)
            emails_found = len([r for r in results if r and r.get('email') and str(r.get('email')).strip() and '@' in str(r.get('email')) and str(r.get('email')) != 'Error occurred'])
            logger.info(f"Statistics calculated: {emails_found}/{total_companies} real emails found")
        except Exception as stats_error:
            logger.error(f"Error calculating statistics: {type(stats_error).__name__}: {str(stats_error)}")
            total_companies = len(results) if results else 0
            emails_found = 0
        
        # Debug: Log first few results to see what we're actually getting
        try:
            debug_results = results[:5]  # First 5 results for debugging
            for i, result in enumerate(debug_results):
                if result and hasattr(result, 'get'):
                    logger.info(f"Debug result {i+1}: company='{result.get('company', 'N/A')}', email='{result.get('email', 'N/A')}', source='{result.get('source', 'N/A')}'")
                else:
                    logger.info(f"Debug result {i+1}: {result}")
        except Exception as debug_error:
            logger.warning(f"Debug logging failed: {str(debug_error)}")
        
        return jsonify({
            'success': True,
            'total': total_companies,
            'found': emails_found,
            'download_url': f'/download/{output_filename}'
        })
        
    except Exception as e:
        error_msg = f"Upload error - Type: {type(e).__name__}, Message: {str(e)}"
        logger.error(error_msg)
        # Provide more helpful error message
        if "NameError" in str(type(e)):
            error_msg = f"Variable not defined: {str(e)}"
        elif "KeyError" in str(type(e)):
            error_msg = f"Missing data field: {str(e)}"
        elif not str(e) or str(e) == "":
            error_msg = f"Unknown error of type: {type(e).__name__}"
        else:
            error_msg = str(e)
        
        return jsonify({'success': False, 'error': error_msg})

@app.route('/download/<filename>')
def download_file(filename):
    try:
        from flask import send_file
        from werkzeug.utils import secure_filename
        import tempfile
        
        secure_name = secure_filename(filename)
        filepath = os.path.join(tempfile.gettempdir(), secure_name)
        
        logger.info(f"Download requested for: {filename}")
        logger.info(f"Looking for file at: {filepath}")
        logger.info(f"File exists: {os.path.exists(filepath)}")
        
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True, download_name=filename)
        else:
            logger.error(f"File not found: {filepath}")
            # List files in temp directory for debugging
            temp_files = os.listdir(tempfile.gettempdir())
            email_files = [f for f in temp_files if 'email_results' in f]
            logger.info(f"Available email result files: {email_files}")
            return jsonify({'error': f'File not found: {filename}'}), 404
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

def find_real_emails_simple(company_name, location_data=None):
    """Simple, proven email extraction - revert to working logic"""
    import requests
    
    # Simple domain generation like last week
    clean_name = re.sub(r'[^a-zA-Z0-9]', '', company_name.lower())
    
    domains_to_try = [
        f"{clean_name}.com",
        f"{company_name.lower().replace(' ', '')}.com",
        f"{company_name.lower().replace(' ', '-')}.com"
    ]
    
    # Add simple variations if company has multiple words
    if ' ' in company_name:
        words = company_name.lower().split()
        if len(words) >= 2 and len(words[0]) >= 3:
            domains_to_try.append(f"{words[0]}.com")
    
    for domain in domains_to_try[:3]:  # Only try 3 domains max
        for protocol in ['https://', 'http://']:
            website = f"{protocol}{domain}"
            
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                response = requests.get(website, headers=headers, timeout=5, allow_redirects=True)
                
                if response.status_code == 200:
                    # Check just 3 key pages like last week
                    pages_to_check = ['', '/contact', '/about']
                    
                    for page in pages_to_check:
                        try:
                            check_url = f"{website.rstrip('/')}{page}" if page else website
                            email = extract_emails_simple(check_url, requests)
                            if email:
                                page_desc = f"{page}" if page else "homepage"
                                return email, f"Found on {website} ({page_desc})"
                        except:
                            continue
                    
                    # Found website but no emails
                    return None, f"Website found ({website}) but no emails"
            except:
                continue
    
    return None, f"No website found for {company_name}"

def extract_emails_simple(url, requests):
    """Simple email extraction like last week"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=4)
        response.raise_for_status()
        
        # Simple email regex
        email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        emails = email_pattern.findall(response.text)
        
        if not emails:
            return None
        
        # Simple filtering like last week
        skip_patterns = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'noreply', 'no-reply', 'example.com']
        
        # Look for business emails first
        for email in emails:
            email_lower = email.lower()
            if not any(skip in email_lower for skip in skip_patterns) and len(email) > 4:
                return email_lower
        
        return None
        
    except Exception as e:
        return None

def process_companies_simple(companies_df, logger):
    """Simple processing like last week that worked"""
    results = []
    processed_companies = set()
    start_time = time.time()
    
    try:
        logger.info(f"Starting simple processing with {len(companies_df)} total rows")
        
        # Simple duplicate removal
        unique_companies = []
        for idx, row in companies_df.iterrows():
            try:
                company_name = clean_company_name(row.get('company', ''))
                
                if not company_name or company_name in processed_companies:
                    continue
                    
                unique_companies.append({'company': company_name, 'original_row': row})
                processed_companies.add(company_name)
                
                if len(unique_companies) >= 200:  # Reduced from 300
                    break
            except Exception:
                continue
        
        logger.info(f"Processing {len(unique_companies)} unique companies")
        
        for i, company_data in enumerate(unique_companies):
            try:
                company_name = company_data['company']
                original_row = company_data['original_row']
                
                logger.info(f"Processing {i+1}/{len(unique_companies)}: {company_name}")
                
                # Simple email search
                email, source = find_real_emails_simple(company_name)
                
                # Create simple result
                result = {
                    'company': str(company_name),
                    'email': str(email) if email else '',
                    'source': str(source) if source else 'No emails found'
                }
                
                # Add original columns
                try:
                    for col in original_row.index:
                        if col.lower() not in ['company']:
                            value = original_row[col]
                            result[col] = str(value) if not pd.isna(value) else ''
                except:
                    pass
                
                results.append(result)
                
            except Exception as e:
                logger.error(f"Error processing {company_data.get('company', 'unknown')}: {str(e)}")
                results.append({
                    'company': str(company_data.get('company', 'Unknown')),
                    'email': '',
                    'source': f'Error: {str(e)}'
                })
        
        total_time = time.time() - start_time
        logger.info(f"Simple processing completed in {total_time:.2f} seconds")
        
        return results
        
    except Exception as e:
        logger.error(f"Error in simple processing: {str(e)}")
        return [{
            'company': 'Processing Failed',
            'email': '',
            'source': f'Error: {str(e)}'
        }]

def clean_company_name(name):
    if not name or str(name).strip() == '' or str(name).lower() in ['nan', 'null', 'none', '', 'n/a']:
        return None
    
    name = str(name).strip()
    
    # Don't clean if the name is too short (likely important)
    if len(name) <= 2:
        return name if name else None
    
    # Only remove common business suffixes, but be more conservative
    suffixes = [' LLC', ' Inc.', ' Inc', ' Corp.', ' Corp', ' Corporation', ' Ltd.', ' Ltd', ' Limited', ' Co.', ' Company']
    for suffix in suffixes:
        if name.upper().endswith(suffix.upper()):
            cleaned = name[:-len(suffix)].strip()
            # Only remove suffix if there's still a substantial company name left
            if len(cleaned) >= 2:  # Reduced from 3 to 2
                name = cleaned
            break
    
    return name if name else None

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