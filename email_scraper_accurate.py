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
<strong>📧 Overview:</strong> Robust fashion-focused email extraction with comprehensive error handling. 3 domains, 10 pages + Instagram fallback. Detailed logging for debugging.<br>
<strong>⚡ Capacity:</strong> Process up to 300 companies in ~4-7 minutes. Each company takes 5-8 seconds with full error recovery and detailed diagnostics.
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
            logger.info("Starting process_companies_hybrid...")
            results = process_companies_hybrid(df, logger)
            logger.info(f"process_companies_hybrid completed with {len(results) if results else 0} results")
        except Exception as process_error:
            logger.error(f"Error in process_companies_hybrid: {type(process_error).__name__}: {str(process_error)}")
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

def generate_business_emails_ai(company_name, location_data=None):
    """Use OpenAI to generate most likely business email addresses"""
    try:
        # Prepare location context
        location_context = ""
        if location_data:
            city = location_data.get('city', '')
            state = location_data.get('state', '')
            country = location_data.get('country', '')
            if city or state or country:
                location_context = f" located in {city}, {state}, {country}".strip(', ')
        
        # Create prompt for OpenAI
        prompt = f"""
Given the company name "{company_name}"{location_context}, generate the 3 most likely business email addresses for this company.

Rules:
1. Generate realistic business email formats (info@, contact@, sales@, hello@, admin@, etc.)
2. Create plausible domain names based on the company name
3. Consider common business naming patterns
4. Use standard TLDs (.com, .us, .co.uk, etc.)
5. If location data is provided, consider country-specific domains

Return ONLY the email addresses, one per line, no explanations:
"""

        # Use the modern OpenAI client
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert at identifying business email patterns. Generate realistic, professional business email addresses."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.3
        )
        
        # Extract emails from response
        emails_text = response.choices[0].message.content
        if not emails_text:
            return None, "No response from AI"
            
        emails_text = emails_text.strip()
        potential_emails = [email.strip() for email in emails_text.split('\n') if email.strip() and '@' in email]
        
        # Validate email format
        email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        valid_emails = []
        
        for email in potential_emails:
            if email_pattern.match(email):
                valid_emails.append(email)
        
        if valid_emails:
            # Return the first (most likely) email
            return valid_emails[0], f"AI-generated: {valid_emails[0]}"
        else:
            return None, "No valid emails generated"
            
    except Exception as e:
        logger.error(f"OpenAI API error for {company_name}: {str(e)}")
        return None, f"AI generation failed: {str(e)}"

def process_companies_hybrid(companies_df, logger):
    """Hybrid AI + web scraping - fast and accurate"""
    results = []
    processed_companies = set()
    start_time = time.time()
    
    try:
        logger.info(f"Starting hybrid AI + web scraping with {len(companies_df)} total rows")
        
        # Remove duplicates and limit to 300 companies
        unique_companies = []
        skipped_empty = 0
        skipped_duplicates = 0
        
        for idx, row in companies_df.iterrows():
            try:
                company_name = clean_company_name(row.get('company', ''))
                
                if not company_name:
                    skipped_empty += 1
                    continue
                    
                if company_name in processed_companies:
                    skipped_duplicates += 1
                    continue
                    
                unique_companies.append({'company': company_name, 'original_row': row})
                processed_companies.add(company_name)
                
                if len(unique_companies) >= 300:
                    break
            except Exception as row_error:
                logger.error(f"Error processing row {idx}: {str(row_error)}")
                skipped_empty += 1
                continue
        
        logger.info(f"Company processing summary: {len(unique_companies)} unique companies, {skipped_empty} empty/invalid, {skipped_duplicates} duplicates")
        
        if not unique_companies:
            logger.warning("No valid companies found to process")
            return []
        
        for i, company_data in enumerate(unique_companies):
            try:
                company_name = company_data['company']
                original_row = company_data['original_row']
                
                company_start_time = time.time()
                logger.info(f"Processing {i+1}/{len(unique_companies)}: {company_name}")
                
                # Prepare location data
                location_data = {}
                try:
                    for col in original_row.index:
                        col_lower = col.lower()
                        if 'city' in col_lower:
                            location_data['city'] = original_row[col]
                        elif 'state' in col_lower:
                            location_data['state'] = original_row[col] 
                        elif 'country' in col_lower:
                            location_data['country'] = original_row[col]
                except Exception as location_error:
                    logger.warning(f"Error extracting location data for {company_name}: {str(location_error)}")
                    location_data = {}
                
                # Use hybrid AI + web scraping
                try:
                    email, source = find_real_emails_enhanced(company_name, location_data)
                except Exception as search_error:
                    logger.error(f"Error in email search for {company_name}: {str(search_error)}")
                    email, source = None, f"Search error: {str(search_error)}"
                
                # DEBUG: Log exactly what was returned
                logger.info(f"DEBUG: Email extraction returned - email: '{email}' (type: {type(email)}), source: '{source}'")
                
                company_time = time.time() - company_start_time
                logger.info(f"Company {company_name} processed in {company_time:.2f}s - Email: {'Found' if email else 'Not found'}")
                
                # Create result with guaranteed structure
                result = {
                    'company': str(company_name) if company_name else '',
                    'email': str(email) if email else '',
                    'source': str(source) if source else 'No emails found'
                }
                
                # Add any additional columns from original data
                try:
                    for col in original_row.index:
                        if col.lower() not in ['company']:
                            # Ensure we handle any data type properly
                            value = original_row[col]
                            if pd.isna(value):
                                result[col] = ''
                            else:
                                result[col] = str(value)
                except Exception as column_error:
                    logger.warning(f"Error adding additional columns for {company_name}: {str(column_error)}")
                
                results.append(result)
                
            except Exception as company_error:
                logger.error(f"Error processing company {company_data.get('company', 'unknown')}: {str(company_error)}")
                
                # Create error result with guaranteed structure
                try:
                    company_name = company_data.get('company', 'Unknown Company')
                    original_row = company_data.get('original_row', {})
                    
                    result = {
                        'company': str(company_name),
                        'email': '',
                        'source': f'Processing error: {str(company_error)}'
                    }
                    
                    # Try to add additional columns even on error
                    try:
                        if hasattr(original_row, 'index'):
                            for col in original_row.index:
                                if col.lower() not in ['company']:
                                    value = original_row[col]
                                    result[col] = str(value) if not pd.isna(value) else ''
                    except:
                        pass
                    
                    results.append(result)
                except Exception as error_result_error:
                    logger.error(f"Could not create error result: {str(error_result_error)}")
                    # Absolute fallback
                    results.append({
                        'company': 'Error Processing Company',
                        'email': '',
                        'source': 'Fatal processing error'
                    })
        
        total_time = time.time() - start_time
        logger.info(f"Hybrid processing completed in {total_time:.2f} seconds")
        
        return results
        
    except Exception as function_error:
        logger.error(f"Fatal error in process_companies_hybrid: {str(function_error)}")
        # Return at least something to prevent undefined errors
        return [{
            'company': 'Processing Failed',
            'email': '',
            'source': f'Function error: {str(function_error)}'
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

def search_engines_fallback(company_name, requests):
    """Search Bing and Yahoo when direct domain guessing fails"""
    try:
        search_engines = [
            f"https://www.bing.com/search?q=\"{company_name}\"+website",
            f"https://search.yahoo.com/search?p=\"{company_name}\"+official+site"
        ]
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
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

def check_instagram_business_email(company_name):
    """Lightweight Instagram business email check (fallback only)"""
    import requests
    import time
    
    try:
        # Generate possible Instagram usernames (max 2 to keep it fast)
        clean_name = re.sub(r'[^a-zA-Z0-9]', '', company_name.lower())
        possible_usernames = []
        
        # Primary username - just company name
        if len(clean_name) >= 3:
            possible_usernames.append(clean_name)
        
        # Secondary username - add common business suffixes
        if len(clean_name) >= 3 and len(clean_name) <= 20:
            for suffix in ['boutique', 'shop']:
                username = f"{clean_name}{suffix}"
                if len(username) <= 30:  # Instagram username limit
                    possible_usernames.append(username)
                    break  # Only add one suffix to keep it fast
        
        # Limit to 2 usernames max for speed
        possible_usernames = possible_usernames[:2]
        
        if not possible_usernames:
            return None, "No valid Instagram usernames generated"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        for username in possible_usernames:
            try:
                # Instagram public page (no API required)
                url = f"https://www.instagram.com/{username}/"
                
                response = requests.get(url, headers=headers, timeout=3)
                
                if response.status_code == 200:
                    content = response.text
                    
                    # Look for email in bio/contact info
                    email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
                    emails = email_pattern.findall(content)
                    
                    if emails:
                        # Filter for business emails
                        business_emails = []
                        skip_patterns = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'aol.com']
                        
                        for email in emails:
                            email_lower = email.lower()
                            if not any(skip in email_lower for skip in skip_patterns) and len(email) > 4:
                                business_emails.append(email_lower)
                        
                        if business_emails:
                            logger.info(f"Found Instagram business email for {company_name}: {business_emails[0]}")
                            return business_emails[0], f"Instagram business email (@{username})"
                
                # Rate limiting - small delay between requests
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Instagram check failed for @{username}: {str(e)}")
                continue
        
        return None, "No Instagram business email found"
        
    except Exception as e:
        logger.error(f"Instagram scraping failed for {company_name}: {str(e)}")
        return None, "Instagram check error"

def generate_enhanced_domains(company_name, country=None, state=None, city=None):
    """Generate focused domain patterns prioritizing most successful patterns"""
    clean_name = company_name.lower().replace(' ', '')
    domains = []
    
    # Skip only if completely empty
    if len(clean_name) <= 1:
        return []
    
    # TOP PRIORITY: Highest success rate patterns (try these first)
    top_priority = [
        f"{clean_name}.com",
        f"{company_name.lower().replace(' ', '-')}.com",
    ]
    
    # Multi-word company priority patterns  
    if ' ' in company_name:
        words = company_name.lower().split()
        if len(words) >= 2:
            first_word = words[0]
            # Add first word if meaningful and reasonable length
            if first_word not in ['the', 'a', 'an'] and len(first_word) >= 2:
                top_priority.append(f"{first_word}.com")
            
            # Acronym for 2-4 words
            if 2 <= len(words) <= 4:
                acronym = ''.join([word[0] for word in words if word and word not in ['the', 'a', 'an']])
                if len(acronym) >= 2:  # Back to 2+ letters
                    top_priority.append(f"{acronym}.com")
    
    domains.extend(top_priority)
    
    # SECONDARY: Business and location patterns
    secondary = []
    
    if country and str(country).lower() in ['usa', 'us', 'united states']:
        secondary.extend([f"{clean_name}.us", f"{clean_name}usa.com"])
    elif country and str(country).lower() in ['canada', 'ca']:
        secondary.append(f"{clean_name}.ca")
    elif country and str(country).lower() in ['uk', 'united kingdom', 'england']:
        secondary.append(f"{clean_name}.co.uk")
    
    # Common business patterns
    secondary.extend([
        f"{clean_name}.net",
        f"{clean_name}inc.com",
        f"{clean_name}.org",
    ])
    
    domains.extend(secondary)
    
    # Remove duplicates but be much less strict about filtering
    seen = set()
    unique_domains = []
    
    for domain in domains:
        if domain and domain not in seen and len(domain) > 3:  # Much more lenient
            seen.add(domain)
            unique_domains.append(domain)
    
    return unique_domains[:10]  # Slightly more domains

def generate_smart_domains_ai(company_name, location_data=None):
    """Use AI to generate highly targeted domain suggestions with better fallbacks"""
    domains = []  # Initialize the domains list
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Enhanced prompt for more accurate domain generation
        location_context = ""
        if location_data:
            parts = []
            if location_data.get('city'):
                parts.append(f"city: {location_data['city']}")
            if location_data.get('state'):
                parts.append(f"state: {location_data['state']}")
            if location_data.get('country'):
                parts.append(f"country: {location_data['country']}")
            if parts:
                location_context = f" (located in {', '.join(parts)})"

        prompt = f"""You are a domain expert helping find the official website for fashion/retail companies.

Company: "{company_name}"{location_context}

Generate the 3 most likely domains for this specific company's official website. Focus on:
1. Exact company name variations (remove spaces, add hyphens, abbreviations)
2. Fashion/boutique/clothing related terms 
3. Common business domain patterns

IMPORTANT: Avoid obviously generic domains like "bad.com", "heart.com", "house.com", "sugar.com", "focused.com", "beyond.com", "angels.com"

Return ONLY the domain names (no http/https), one per line.
Example format:
piperandscoot.com
piper-scoot.com
piperandscootboutique.com"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.1
        )
        
        response_content = response.choices[0].message.content
        if response_content:
            suggestions = response_content.strip().split('\n')
            
            for suggestion in suggestions:
                domain = suggestion.strip().lower()
                # Remove any prefixes and clean
                domain = domain.replace('http://', '').replace('https://', '').replace('www.', '')
                if domain and '.' in domain and len(domain) > 4:
                    # Avoid obviously wrong generic domains
                    generic_domains = ['bad.com', 'heart.com', 'house.com', 'sugar.com', 'focused.com', 'beyond.com', 'angels.com']
                    if domain not in generic_domains:
                        domains.append(domain)
        
    except Exception as ai_error:
        logger.error(f"AI domain generation failed for {company_name}: {str(ai_error)}")
    
    # Add manual fallback domains if AI didn't generate enough or failed
    if len(domains) < 3:
        try:
            clean_name = re.sub(r'[^a-zA-Z0-9\s]', '', company_name.lower())
            clean_name = re.sub(r'\s+', '', clean_name)
            
            fallback_domains = [
                f"{clean_name}.com",
                f"{clean_name}boutique.com",
                f"{clean_name}shop.com"
            ]
            
            for fallback in fallback_domains:
                if fallback not in domains and len(domains) < 3:
                    domains.append(fallback)
        except Exception as fallback_error:
            logger.error(f"Fallback domain generation failed for {company_name}: {str(fallback_error)}")
    
    # Ensure we always return at least one domain
    if not domains:
        try:
            simple_name = re.sub(r'[^a-zA-Z0-9]', '', company_name.lower())
            domains = [f"{simple_name}.com"]
        except:
            domains = ["example.com"]  # Last resort
    
    logger.info(f"Generated domains for {company_name}: {domains}")
    return domains[:3]  # Max 3 domains

def extract_real_emails_comprehensive(url, requests, company_name):
    """Comprehensive email extraction with relaxed validation"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=4)
        response.raise_for_status()
        
        content = response.text.lower()  # Convert to lowercase for validation
        
        # Much more relaxed company validation for higher success rate
        company_words = re.sub(r'[^a-zA-Z0-9\s]', '', company_name.lower()).split()
        company_words = [word for word in company_words if len(word) > 2]  # Remove short words
        
        # Check if company name appears in page content
        if company_words and len(company_words) >= 2:  # Only validate if multiple words
            found_company_words = sum(1 for word in company_words if word in content)
            company_match_ratio = found_company_words / len(company_words)
            
            # Very relaxed validation: If less than 10% of company words found, this might be wrong website
            # (was 20%, now 10% for much higher success rate)
            if company_match_ratio < 0.1:
                logger.info(f"DEBUG: Very low company match for {company_name} on {url} ({company_match_ratio:.2f})")
                # Still allow single-word companies or if it's a homepage
                if len(company_words) > 1 and '/contact' not in url and '/wholesale' not in url:
                    return None
        
        # Extract emails with multiple patterns
        email_patterns = [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Standard
            r'mailto:([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})',  # Mailto links
        ]
        
        all_emails = []
        original_content = response.text  # Keep original case for email extraction
        
        for pattern in email_patterns:
            found_emails = re.findall(pattern, original_content, re.IGNORECASE)
            if isinstance(found_emails, list):
                all_emails.extend(found_emails)
        
        logger.info(f"DEBUG: Found {len(all_emails)} raw emails on {url}: {all_emails[:3] if all_emails else 'None'}")
        
        if not all_emails:
            return None
        
        # Relaxed filtering - only skip obvious spam/personal emails
        skip_patterns = [
            'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'aol.com',
            'noreply', 'no-reply', 'donotreply', 'mailer-daemon', 'postmaster',
            'example.com', 'test.com', 'localhost', 'youremail.com', 'firstname@',
            'cognitive.ai', 'mlb.com', 'nytimes.com', 'sentry', 'wixpress.com',
            '.png', '.jpg', '.jpeg', '.gif', '.webp', 'img_', 'flags@'
        ]
        
        # Prioritize business-looking emails (with wholesale first for fashion companies)
        priority_prefixes = ['wholesale@', 'info@', 'contact@', 'sales@', 'support@', 'hello@', 'orders@']
        
        # First pass: look for priority emails (relaxed domain matching)
        for email in all_emails:
            email_clean = str(email).strip().lower()
            if (len(email_clean) > 4 and 
                '@' in email_clean and 
                '.' in email_clean.split('@')[1] and
                not any(skip in email_clean for skip in skip_patterns)):
                
                # More relaxed domain matching
                email_domain = email_clean.split('@')[1]
                site_domain = url.replace('http://', '').replace('https://', '').split('/')[0]
                
                # Accept emails if they're business-like OR from related domains
                if (any(email_clean.startswith(prefix) for prefix in priority_prefixes) or
                    email_domain in site_domain or site_domain in email_domain):
                    logger.info(f"DEBUG: Returning priority email from {url}: {email_clean}")
                    return email_clean
        
        # Second pass: any valid business email (even more relaxed)
        for email in all_emails:
            email_clean = str(email).strip().lower()
            if (len(email_clean) > 4 and 
                '@' in email_clean and 
                '.' in email_clean.split('@')[1] and
                not any(skip in email_clean for skip in skip_patterns)):
                
                logger.info(f"DEBUG: Returning relaxed validation email from {url}: {email_clean}")
                return email_clean
        
        logger.info(f"DEBUG: All emails filtered out from {url}")
        return None
        
    except Exception as e:
        logger.error(f"DEBUG: Error extracting emails from {url}: {str(e)}")
        return None

def find_real_emails_enhanced(company_name, location_data=None):
    """Enhanced email finding with web scraping + Instagram fallback"""
    import requests
    
    website_found = None  # Initialize the variable
    
    # First: Try web scraping (primary method)
    domains_to_try = generate_smart_domains_ai(company_name, location_data)
    
    for domain in domains_to_try:
        for protocol in ['https://', 'http://']:
            website = f"{protocol}{domain}"
            
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                response = requests.get(website, headers=headers, timeout=4, allow_redirects=True)
                
                if response.status_code == 200:
                    website_found = website  # Store the working website
                    
                    # Check pages prioritizing wholesale and contact (fashion-focused)
                    pages_to_check = [
                        '/wholesale',           # #1 priority for fashion companies
                        '/contact',            # #2 priority
                        '/contact-us',         # Common variation
                        '/wholesale-inquiry',  # Fashion-specific
                        '/trade',              # Another wholesale variation
                        '/b2b',               # Business-to-business
                        '',                   # Homepage
                        '/about',             # About page
                        '/about-us',          # About variation
                        '/support'            # Support page
                    ]
                    
                    for page in pages_to_check:
                        try:
                            check_url = f"{website.rstrip('/')}{page}" if page else website
                            email = extract_real_emails_comprehensive(check_url, requests, company_name)
                            if email:
                                page_desc = f"{page}" if page else "homepage"
                                return email, f"Real email from {website} ({page_desc})"
                        except Exception as page_error:
                            logger.error(f"Error checking page {page} for {company_name}: {str(page_error)}")
                            continue
                    
                    # Found website but no emails - break to try Instagram
                    break
            except Exception as domain_error:
                logger.error(f"Error checking domain {domain} for {company_name}: {str(domain_error)}")
                continue
    
    # Fallback: Try Instagram if web scraping found no emails
    try:
        logger.info(f"Web scraping found no emails for {company_name}, trying Instagram fallback...")
        instagram_email, instagram_source = check_instagram_business_email(company_name)
        
        if instagram_email:
            return instagram_email, instagram_source
    except Exception as instagram_error:
        logger.error(f"Instagram fallback failed for {company_name}: {str(instagram_error)}")
    
    # Return appropriate message based on what was found
    if website_found:
        return None, f"Website found ({website_found}) but no emails detected (Instagram also checked)"
    else:
        return None, f"No website found for {company_name} (Instagram also checked)"

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