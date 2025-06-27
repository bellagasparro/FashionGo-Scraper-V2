from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import os
import time
from urllib.parse import urljoin, urlparse
import logging
from werkzeug.utils import secure_filename
import io

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Create uploads directory if it doesn't exist
os.makedirs('uploads', exist_ok=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Email regex pattern
EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')

def clean_company_name(name):
    """Clean and normalize company name for better search results"""
    if pd.isna(name) or name is None or str(name).strip() == '':
        return None
    
    name = str(name).strip()
    # Remove common suffixes that might interfere with search
    suffixes = [' LLC', ' Inc', ' Corp', ' Corporation', ' Ltd', ' Limited', ' Co', ' Company']
    for suffix in suffixes:
        if name.upper().endswith(suffix.upper()):
            name = name[:-len(suffix)].strip()
    
    return name if name else None

def find_emails_on_page(url, timeout=10):
    """Find email addresses on a given webpage"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        # Find emails in the HTML content
        emails = set(EMAIL_PATTERN.findall(response.text))
        
        # Filter out common false positives
        filtered_emails = []
        for email in emails:
            email_lower = email.lower()
            if not any(x in email_lower for x in ['example.com', 'test.com', 'placeholder', 'yoursite', 'yourdomain']):
                filtered_emails.append(email)
        
        return list(set(filtered_emails))
    
    except Exception as e:
        logger.error(f"Error fetching {url}: {str(e)}")
        return []

def search_company_website(company_name):
    """Search for company website using Google search"""
    try:
        if not company_name:
            return None
            
        # Clean company name
        clean_name = clean_company_name(company_name)
        if not clean_name:
            return None
            
        # Simple search query
        search_query = f"{clean_name} official website"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Use DuckDuckGo instead of Google to avoid blocking
        search_url = f"https://duckduckgo.com/html/?q={search_query}"
        
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for result links
        links = soup.find_all('a', {'class': 'result__a'})
        
        for link in links[:3]:  # Check first 3 results
            href = link.get('href')
            if href and 'http' in href:
                return href
                
        return None
        
    except Exception as e:
        logger.error(f"Error searching for {company_name}: {str(e)}")
        return None

def find_company_email(company_name):
    """Find email for a company by searching their website"""
    try:
        if not company_name:
            return None, None
            
        logger.info(f"Searching for emails for: {company_name}")
        
        # Search for company website
        website = search_company_website(company_name)
        if not website:
            logger.info(f"No website found for {company_name}")
            return None, None
        
        logger.info(f"Found website for {company_name}: {website}")
        
        # Check main page
        emails = find_emails_on_page(website)
        if emails:
            return emails[0], f"Main page: {website}"
        
        # Try common contact pages
        base_url = website.rstrip('/')
        contact_pages = ['/contact', '/contact-us', '/about', '/about-us']
        
        for page in contact_pages:
            try:
                contact_url = base_url + page
                emails = find_emails_on_page(contact_url)
                if emails:
                    return emails[0], f"Contact page: {contact_url}"
            except:
                continue
        
        return None, f"No emails found on {website}"
        
    except Exception as e:
        logger.error(f"Error finding email for {company_name}: {str(e)}")
        return None, f"Error: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'}), 200

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Read the file
        try:
            if filename.endswith('.csv'):
                df = pd.read_csv(filepath)
            elif filename.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(filepath)
            else:
                return jsonify({'error': 'Unsupported file format. Please upload CSV or Excel files.'}), 400
        except Exception as e:
            return jsonify({'error': f'Error reading file: {str(e)}'}), 400
        
        # Clean up uploaded file
        os.remove(filepath)
        
        # Detect company name column
        company_column = None
        possible_columns = ['companyName', 'shipToCompanyName', 'company_name', 'Company Name', 'Company', 'Name']
        
        for col in possible_columns:
            if col in df.columns:
                company_column = col
                break
        
        if not company_column:
            available_columns = list(df.columns)
            return jsonify({
                'error': f'Could not find company name column. Available columns: {available_columns}. Please ensure your file has one of these columns: {possible_columns}'
            }), 400
        
        # Process companies
        results = []
        total_companies = len(df)
        
        logger.info(f"Processing {total_companies} companies using column: {company_column}")
        
        for index, row in df.iterrows():
            try:
                # Skip empty rows
                if pd.isna(row[company_column]) or str(row[company_column]).strip() == '':
                    logger.info(f"Skipping row {index + 1}: empty company name")
                    continue
                
                company_name = str(row[company_column]).strip()
                logger.info(f"Processing company {index + 1}/{total_companies}: {company_name}")
                
                # Find email
                email, source = find_company_email(company_name)
                
                # Create result row
                result_row = row.to_dict()
                result_row['found_email'] = email if email else 'Not found'
                result_row['email_source'] = source if source else 'N/A'
                result_row['processed_company_name'] = company_name
                
                results.append(result_row)
                
                # Add delay to be respectful to websites
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error processing row {index + 1}: {str(e)}")
                # Continue with next row instead of stopping
                result_row = row.to_dict()
                result_row['found_email'] = 'Error'
                result_row['email_source'] = f'Error: {str(e)}'
                result_row['processed_company_name'] = str(row[company_column]) if not pd.isna(row[company_column]) else 'N/A'
                results.append(result_row)
                continue
        
        # Create results DataFrame
        results_df = pd.DataFrame(results)
        
        # Save results to CSV
        output_filename = f"email_results_{int(time.time())}.csv"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        results_df.to_csv(output_path, index=False)
        
        # Calculate statistics
        total_processed = len(results_df)
        emails_found = len(results_df[results_df['found_email'] != 'Not found'])
        success_rate = (emails_found / total_processed * 100) if total_processed > 0 else 0
        
        return jsonify({
            'success': True,
            'total_companies': total_processed,
            'emails_found': emails_found,
            'success_rate': round(success_rate, 1),
            'download_url': f'/download/{output_filename}',
            'company_column_used': company_column
        })
        
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port) 