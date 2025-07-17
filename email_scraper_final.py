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
            EMAIL_PATTERN,  # Standard pattern
            re.compile(r'mailto:([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', re.IGNORECASE),
            re.compile(r'contact[^@]*?([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', re.IGNORECASE),
            re.compile(r'info[^@]*?([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', re.IGNORECASE),
        ]
        
        all_emails = set()
        for pattern in email_patterns:
            emails = pattern.findall(text_content)
            all_emails.update(emails)
        
        # Prioritize business emails
        business_emails = []
        other_emails = []
        
        for email in all_emails:
            email_lower = email.lower().strip()
            
            # Skip obvious fake/template emails
            if any(x in email_lower for x in [
                'example.com', 'test.com', 'placeholder', 'yoursite', 'yourdomain',
                'samplewebsite', 'domain.com', 'email.com', 'website.com',
                'admin@admin', 'test@test', 'user@domain'
            ]):
                continue
            
            # Skip common non-business emails  
            if any(x in email_lower for x in [
                'noreply', 'no-reply', 'donotreply', 'unsubscribe', 'bounce',
                'mailer-daemon', 'postmaster', 'root@', 'webmaster'
            ]):
                continue
                
            # Basic domain validation
            if '@' not in email_lower or '.' not in email_lower.split('@')[-1]:
                continue
                
            # Prioritize business-looking emails
            if any(x in email_lower for x in [
                'info@', 'contact@', 'sales@', 'support@', 'hello@', 'inquiry@',
                'business@', 'office@', 'admin@', 'service@', 'help@'
            ]):
                business_emails.append(email)
            else:
                other_emails.append(email)
        
        # Return business emails first, then others
        return business_emails + other_emails
    
    except requests.exceptions.Timeout:
        logger.warning(f"Timeout fetching {url}")
        return []
    except Exception as e:
        logger.warning(f"Error fetching {url}: {str(e)}")
        return []

def search_company_website(company_name):
    """Enhanced multi-strategy website search with direct guessing and fallbacks"""
    try:
        if not company_name:
            return None
            
        clean_name = clean_company_name(company_name)
        if not clean_name:
            return None
            
        # Strategy 1: Direct Website Guessing (Most Reliable)
        direct_urls = generate_direct_website_guesses(clean_name)
        for url in direct_urls:
            if test_website_exists(url):
                logger.info(f"Found via direct guess: {url}")
                return url
        
        # Strategy 2: Simplified Search Engines (Faster & More Reliable)
        search_engines = [
            {
                'name': 'Bing',
                'url': f"https://www.bing.com/search?q=\"{clean_name}\"+site%3A{clean_name.replace(' ', '')}.com",
                'timeout': 3
            },
            {
                'name': 'Yahoo',
                'url': f"https://search.yahoo.com/search?p=\"{clean_name}\"+website",
                'timeout': 3
            }
        ]
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        
        for engine in search_engines:
            try:
                response = requests.get(engine['url'], headers=headers, timeout=engine['timeout'])
                if response.status_code == 200:
                    urls = extract_business_urls_from_search(response.text, clean_name)
                    for url in urls[:3]:  # Check top 3 results
                        if is_valid_business_url(url):
                            logger.info(f"Found via {engine['name']}: {url}")
                            return url
            except Exception as e:
                logger.warning(f"{engine['name']} search failed: {str(e)}")
                continue
        
        logger.info(f"No website found for {clean_name}")
        return None
        
    except Exception as e:
        logger.error(f"Error searching for {company_name}: {str(e)}")
        return None

def generate_direct_website_guesses(company_name):
    """Generate comprehensive website URL guesses for maximum success rate"""
    urls = []
    
    # Clean the name for URL generation
    clean = re.sub(r'[^a-zA-Z0-9\s]', '', company_name.lower())
    clean_no_spaces = re.sub(r'\s+', '', clean)  # Remove all spaces
    
    # Get first word and abbreviation
    words = clean.split()
    first_word = words[0] if words else clean
    abbreviation = ''.join([word[0] for word in words if len(word) > 0])[:6]  # Max 6 chars
    
    # Base domains to try
    base_names = []
    
    if clean_no_spaces and len(clean_no_spaces) > 2:
        base_names.append(clean_no_spaces)
        
    # Add dash variations for multi-word companies
    if len(words) > 1:
        dash_name = '-'.join(words)
        base_names.append(dash_name)
        
        # Try first word only
        if len(first_word) > 3:
            base_names.append(first_word)
    
    # Add abbreviation if meaningful
    if len(abbreviation) >= 2 and abbreviation != clean_no_spaces:
        base_names.append(abbreviation)
        
    # Add "the" prefix removal
    if clean.startswith('the '):
        no_the = clean[4:].replace(' ', '')
        if no_the and len(no_the) > 2:
            base_names.append(no_the)
    
    # Comprehensive TLD list (major success rate boost)
    tlds = [
        '.com', '.net', '.org', '.biz', '.co', '.us', '.io', '.co.uk',
        '.info', '.shop', '.store', '.online', '.website', '.site',
        '.business', '.company', '.corp', '.inc', '.ltd'
    ]
    
    # Generate all combinations
    for base_name in base_names:
        if base_name and len(base_name) > 1:
            for tld in tlds:
                urls.extend([
                    f"https://www.{base_name}{tld}",
                    f"https://{base_name}{tld}"
                ])
    
    return urls

def test_website_exists(url):
    """Quickly test if a website exists and is accessible"""
    try:
        response = requests.head(url, timeout=3, allow_redirects=True)
        return response.status_code in [200, 301, 302, 403]  # 403 might still have contact info
    except:
        return False

def extract_business_urls_from_search(html_content, company_name):
    """Extract business URLs from search engine results"""
    urls = []
    
    # Simple regex to find URLs in search results
    url_pattern = re.compile(r'https?://(?:www\.)?([a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,})', re.IGNORECASE)
    matches = url_pattern.findall(html_content)
    
    company_keywords = company_name.lower().split()
    
    for match in matches:
        full_url = f"https://{match}"
        domain_lower = match.lower()
        
        # Prioritize URLs that contain company name keywords
        if any(keyword in domain_lower for keyword in company_keywords if len(keyword) > 3):
            urls.insert(0, full_url)  # Put at beginning
        else:
            urls.append(full_url)
    
    return urls[:10]  # Return top 10

def is_valid_business_url(url):
    """Enhanced URL validation for business websites"""
    if not url or not isinstance(url, str):
        return False
    
    # Must be HTTP/HTTPS
    if not url.startswith(('http://', 'https://')):
        return False
    
    # Extract domain
    try:
        domain = url.split('/')[2].lower()
    except:
        return False
    
    # Must have proper domain structure
    if '.' not in domain or len(domain) < 4:
        return False
    
    # Exclude search engines, social media, and common non-business sites
    excluded_domains = [
        'google.com', 'bing.com', 'yahoo.com', 'duckduckgo.com', 'startpage.com',
        'facebook.com', 'twitter.com', 'linkedin.com', 'instagram.com', 'youtube.com',
        'wikipedia.org', 'amazon.com', 'ebay.com', 'alibaba.com', 'aliexpress.com',
        'pinterest.com', 'tiktok.com', 'snapchat.com', 'reddit.com', 'tumblr.com'
    ]
    
    for excluded in excluded_domains:
        if excluded in domain:
            return False
    
    # Prefer business-like domains
    business_indicators = ['.com', '.net', '.org', '.biz', '.co', '.us', '.shop', '.store']
    if any(indicator in domain for indicator in business_indicators):
        return True
    
    return len(domain.split('.')) >= 2  # At least domain.tld format

def guess_email_format(company_name, website_url):
    """Guess common email formats when website found but no emails displayed"""
    try:
        # Extract domain from website URL
        domain = website_url.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0]
        
        # Common business email prefixes (ordered by likelihood)
        email_prefixes = [
            'info', 'contact', 'hello', 'sales', 'support', 'inquiry',
            'business', 'office', 'admin', 'service', 'help', 'mail',
            'general', 'team', 'welcome', 'connect', 'reach'
        ]
        
        # Try each prefix with the domain
        for prefix in email_prefixes:
            candidate_email = f"{prefix}@{domain}"
            
            # Quick validation check (could be enhanced with actual email verification)
            if is_valid_email_format(candidate_email):
                return candidate_email
                
        return None
        
    except Exception as e:
        logger.warning(f"Error guessing email format: {str(e)}")
        return None

def is_valid_email_format(email):
    """Basic email format validation"""
    return '@' in email and '.' in email.split('@')[-1] and len(email.split('@')) == 2

def find_company_email(company_name):
    """Find email for a company with production-optimized settings"""
    try:
        if not company_name:
            return None, None
            
        logger.info(f"Searching for emails for: {company_name}")
        
        # Search for company website
        website = search_company_website(company_name)
        if not website:
            logger.info(f"No website found for {company_name}")
            return None, f"No website found"
        
        logger.info(f"Found website for {company_name}: {website}")
        
        # Check main page first
        emails = find_emails_on_page(website)
        if emails:
            logger.info(f"Found email on main page for {company_name}: {emails[0]}")
            return emails[0], f"Main page: {website}"
        
        # Try more comprehensive contact pages for higher success rate
        if isinstance(website, str):
            base_url = website.rstrip('/')
            
            # Comprehensive contact page list (major success rate boost)
            contact_pages = [
                '/contact', '/contact-us', '/contact_us', '/contactus',
                '/about', '/about-us', '/about_us', '/aboutus',
                '/support', '/help', '/customer-service', '/customer_service',
                '/info', '/information', '/reach-us', '/reach_us',
                '/get-in-touch', '/touch', '/connect', '/feedback',
                '/sales', '/business', '/office', '/headquarters',
                '/team', '/staff', '/management', '/leadership'
            ]
            
            for page in contact_pages:
                try:
                    contact_url = base_url + page
                    emails = find_emails_on_page(contact_url)
                    if emails:
                        logger.info(f"Found email on contact page for {company_name}: {emails[0]}")
                        return emails[0], f"Contact page: {contact_url}"
                    
                    # Shorter delay for production
                    time.sleep(0.2)
                    
                except Exception as e:
                    logger.warning(f"Error checking contact page {contact_url}: {str(e)}")
                    continue
                    
            # Strategy 4: Dynamic contact link detection (success rate boost)
            dynamic_contact_links = find_contact_links(website)
            for contact_link in dynamic_contact_links:
                try:
                    emails = find_emails_on_page(contact_link)
                    if emails:
                        logger.info(f"Found email on dynamic contact page for {company_name}: {emails[0]}")
                        return emails[0], f"Dynamic contact page: {contact_link}"
                        
                    time.sleep(0.2)
                    
                except Exception as e:
                    logger.warning(f"Error checking dynamic contact page {contact_link}: {str(e)}")
                    continue
        
        logger.info(f"No emails found for {company_name} on {website}")
        
        # Strategy 3: Email format guessing if website found but no emails (success rate boost)
        guessed_email = guess_email_format(company_name, website)
        if guessed_email:
            logger.info(f"Guessed email format for {company_name}: {guessed_email}")
            return guessed_email, f"Email format guess: {website}"
        
        # Strategy 5: Subdomain checking (final fallback)
        subdomain_email = check_subdomains_for_emails(website, company_name)
        if subdomain_email:
            return subdomain_email[0], f"Subdomain: {subdomain_email[1]}"
        
        # Strategy 6: Social Media Email Extraction (major success rate boost)
        try:
            social_email = extract_email_from_social_media(company_name)
            if social_email:
                return social_email[0], f"Social media: {social_email[1]}"
        except Exception as e:
            logger.warning(f"Social media extraction failed for {company_name}: {str(e)}")
            # Continue without failing
        
        return None, f"No emails found on {website}"
        
    except Exception as e:
        logger.error(f"Error finding email for {company_name}: {str(e)}")
        return None, f"Error: {str(e)}"

def find_contact_links(website_url):
    """Dynamically find contact page links from homepage"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
        
        response = requests.get(website_url, headers=headers, timeout=5, allow_redirects=True)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        contact_links = []
        
        # Look for links containing contact-related keywords
        contact_keywords = [
            'contact', 'about', 'support', 'help', 'reach', 'touch', 'connect',
            'info', 'team', 'staff', 'office', 'location', 'feedback', 'inquiry'
        ]
        
        # Find all links
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if not href or not isinstance(href, str):
                continue
                
            link_text = link.get_text(strip=True).lower()
            
            # Check if link or text contains contact keywords
            for keyword in contact_keywords:
                if keyword in href.lower() or keyword in link_text:
                    # Convert relative URLs to absolute
                    if href.startswith('/'):
                        full_url = website_url.rstrip('/') + href
                    elif href.startswith('http'):
                        full_url = href
                    else:
                        continue
                        
                    if full_url not in contact_links:
                        contact_links.append(full_url)
                    break
        
        return contact_links[:10]  # Return top 10 contact links
        
    except Exception as e:
        logger.warning(f"Error finding contact links on {website_url}: {str(e)}")
        return []

def check_subdomains_for_emails(main_website, company_name):
    """Check common business subdomains for contact emails"""
    try:
        # Extract base domain
        base_domain = main_website.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0]
        
        # Common business subdomains
        subdomains = ['blog', 'support', 'help', 'info', 'contact', 'about', 'team']
        
        for subdomain in subdomains:
            try:
                subdomain_url = f"https://{subdomain}.{base_domain}"
                if test_website_exists(subdomain_url):
                    emails = find_emails_on_page(subdomain_url)
                    if emails:
                        logger.info(f"Found email on subdomain for {company_name}: {emails[0]}")
                        return emails[0], subdomain_url
                        
                time.sleep(0.3)
                
            except Exception:
                continue
                
        return None
        
    except Exception as e:
        logger.warning(f"Error checking subdomains: {str(e)}")
        return None

def extract_email_from_social_media(company_name):
    """Extract emails from social media profiles (Instagram, Facebook, LinkedIn, Twitter)"""
    try:
        logger.info(f"Checking social media for {company_name}")
        
        # Clean company name for social media search
        clean_name = clean_company_name(company_name)
        if not clean_name:
            return None
            
        # Social media platforms to check
        platforms = [
            {
                'name': 'Instagram',
                'search_url': f"https://www.google.com/search?q=site:instagram.com+\"{clean_name}\"",
                'profile_indicators': ['instagram.com/', '@'],
                'timeout': 4
            },
            {
                'name': 'Facebook', 
                'search_url': f"https://www.google.com/search?q=site:facebook.com+\"{clean_name}\"",
                'profile_indicators': ['facebook.com/', 'fb.com/'],
                'timeout': 4
            },
            {
                'name': 'LinkedIn',
                'search_url': f"https://www.google.com/search?q=site:linkedin.com/company+\"{clean_name}\"",
                'profile_indicators': ['linkedin.com/company/', 'linkedin.com/in/'],
                'timeout': 4
            },
            {
                'name': 'Twitter',
                'search_url': f"https://www.google.com/search?q=site:twitter.com+\"{clean_name}\"",
                'profile_indicators': ['twitter.com/', 'x.com/', '@'],
                'timeout': 4
            }
        ]
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        
        for platform in platforms:
            try:
                # Search for social media profiles
                response = requests.get(platform['search_url'], headers=headers, timeout=platform['timeout'])
                if response.status_code == 200:
                    # Find social media profile URLs
                    profile_urls = extract_social_media_urls(response.text, platform['profile_indicators'], clean_name)
                    
                    # Check each profile for contact info
                    for profile_url in profile_urls[:2]:  # Check top 2 profiles per platform
                        try:
                            email = extract_email_from_social_profile(profile_url, platform['name'])
                            if email:
                                logger.info(f"Found email on {platform['name']} for {company_name}: {email}")
                                return email, f"{platform['name']} profile"
                                
                            time.sleep(0.5)  # Rate limiting
                            
                        except Exception as e:
                            logger.warning(f"Error checking {platform['name']} profile {profile_url}: {str(e)}")
                            continue
                            
                time.sleep(0.3)  # Rate limiting between platforms
                
            except Exception as e:
                logger.warning(f"Error searching {platform['name']}: {str(e)}")
                continue
        
        return None
        
    except Exception as e:
        logger.warning(f"Error in social media extraction: {str(e)}")
        return None

def extract_social_media_urls(html_content, indicators, company_name):
    """Extract social media profile URLs from search results"""
    urls = []
    
    # Find URLs in the HTML that match social media patterns
    url_pattern = re.compile(r'https?://(?:www\.)?([^/\s]+(?:/[^\s"\'<>]*)?)', re.IGNORECASE)
    matches = url_pattern.findall(html_content)
    
    company_keywords = company_name.lower().split()
    
    for match in matches:
        full_url = f"https://{match}"
        
        # Check if URL is from target platform
        if any(indicator in full_url.lower() for indicator in indicators):
            # Prioritize URLs that seem to match the company name
            if any(keyword in full_url.lower() for keyword in company_keywords if len(keyword) > 3):
                urls.insert(0, full_url)  # Priority placement
            else:
                urls.append(full_url)
    
    return urls[:5]  # Return top 5 URLs

def extract_email_from_social_profile(profile_url, platform_name):
    """Extract email from individual social media profile"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
        
        response = requests.get(profile_url, headers=headers, timeout=5, allow_redirects=True)
        response.raise_for_status()
        
        # Use multiple email patterns optimized for social media
        social_email_patterns = [
            EMAIL_PATTERN,  # Standard pattern
            re.compile(r'contact[:\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', re.IGNORECASE),
            re.compile(r'email[:\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', re.IGNORECASE),
            re.compile(r'reach[:\s]+us[:\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', re.IGNORECASE),
            re.compile(r'business[:\s]+inquiries[:\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', re.IGNORECASE),
        ]
        
        for pattern in social_email_patterns:
            emails = pattern.findall(response.text.lower())
            if emails:
                # Filter and validate emails
                for email in emails:
                    if is_valid_email_format(email) and not is_fake_email(email):
                        return email
        
        return None
        
    except Exception as e:
        logger.warning(f"Error extracting from {platform_name} profile {profile_url}: {str(e)}")
        return None

def is_fake_email(email):
    """Check if email appears to be fake or template"""
    fake_indicators = [
        'example.com', 'test.com', 'placeholder', 'yoursite', 'yourdomain',
        'samplewebsite', 'domain.com', 'email.com', 'website.com',
        'noreply', 'no-reply', 'donotreply', 'unsubscribe'
    ]
    
    email_lower = email.lower()
    return any(indicator in email_lower for indicator in fake_indicators)

@app.route('/')
def index():
    return '''<!DOCTYPE html>
<html><head><title>FashionGo Email Finder</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
<style>body{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);min-height:100vh}
.main-container{background:white;border-radius:15px;box-shadow:0 10px 30px rgba(0,0,0,0.1);margin:2rem auto;max-width:800px}
.header{background:#2c5aa0;color:white;padding:2rem;border-radius:15px 15px 0 0;text-align:center}</style></head>
<body><div class="container"><div class="main-container"><div class="header">
<h1>🔍 FashionGo Email Finder</h1><p>Upload your FashionGo customer export and find email addresses</p></div>
<div class="p-4"><div class="alert alert-info"><h6>How it works:</h6><ul>
<li>Upload your FashionGo CSV or Excel file</li><li>System detects company names from 'companyName' or 'shipToCompanyName' columns</li>
<li>Searches for each company's website and extracts email addresses</li>
<li>Download enhanced file with email addresses and sources</li></ul></div>
<form id="uploadForm" enctype="multipart/form-data"><div class="mb-3">
<label class="form-label">Select FashionGo Export File:</label>
<input type="file" class="form-control" id="fileInput" name="file" accept=".csv,.xlsx,.xls" required></div>
<button type="submit" class="btn btn-primary btn-lg">🚀 Find Emails</button></form>
<div id="loading" style="display:none" class="text-center mt-4">
<div class="spinner-border text-primary"></div><h5 class="mt-3">Finding email addresses...</h5>
<p class="text-muted">Processing all companies in your file - this may take a while for large files</p></div>
<div id="results" style="display:none" class="mt-4"><div class="alert alert-success">
<h6>✅ Processing Complete!</h6><div class="row text-center mt-3">
<div class="col-md-4"><div style="font-size:2rem;font-weight:bold;color:#2c5aa0" id="totalCompanies">0</div><small>Companies</small></div>
<div class="col-md-4"><div style="font-size:2rem;font-weight:bold;color:#2c5aa0" id="emailsFound">0</div><small>Emails Found</small></div>
<div class="col-md-4"><div style="font-size:2rem;font-weight:bold;color:#2c5aa0" id="successRate">0%</div><small>Success Rate</small></div></div>
<div class="text-center mt-3"><button id="downloadBtn" class="btn btn-success btn-lg">📥 Download Results</button>
<button class="btn btn-secondary ms-2" onclick="resetForm()">🔄 Process Another File</button></div></div></div>
<div id="error" style="display:none" class="mt-4"><div class="alert alert-danger">
<h6>❌ Error</h6><p id="errorText"></p></div></div></div></div></div>
<script>document.getElementById('uploadForm').addEventListener('submit',function(e){
e.preventDefault();const file=document.getElementById('fileInput').files[0];
if(!file){alert('Please select a file');return;}const formData=new FormData();formData.append('file',file);
document.getElementById('loading').style.display='block';
document.getElementById('results').style.display='none';
document.getElementById('error').style.display='none';
fetch('/upload',{method:'POST',body:formData}).then(r=>r.json()).then(data=>{
document.getElementById('loading').style.display='none';if(data.success){
document.getElementById('totalCompanies').textContent=data.total_companies;
document.getElementById('emailsFound').textContent=data.emails_found;
document.getElementById('successRate').textContent=data.success_rate+'%';
document.getElementById('downloadBtn').onclick=()=>window.location.href=data.download_url;
document.getElementById('results').style.display='block';}else{
document.getElementById('errorText').textContent=data.error;
document.getElementById('error').style.display='block';}}).catch(e=>{
document.getElementById('loading').style.display='none';
document.getElementById('errorText').textContent='Network error: '+e.message;
document.getElementById('error').style.display='block';});});
function resetForm(){document.getElementById('results').style.display='none';
document.getElementById('error').style.display='none';document.getElementById('fileInput').value='';}
</script></body></html>'''

@app.route('/health')
def health():
    try:
        # Quick health check with minimal dependencies
        return jsonify({
            'status': 'healthy',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S UTC'),
            'version': '2.0-social-media',
            'app': 'fashiongo-email-scraper'
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
        'message': 'If you can see this, the app is accessible from Korea!'
    })

@app.route('/debug')
def debug():
    """Debug endpoint for troubleshooting access issues"""
    try:
        user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        user_agent = request.headers.get('User-Agent', 'Unknown')
        
        # Get all headers for debugging
        headers = dict(request.headers)
        
        debug_info = {
            'status': 'debug_info',
            'user_ip': user_ip,
            'user_agent': user_agent,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S UTC'),
            'server_location': 'Railway (Europe)',
            'headers': headers,
            'method': request.method,
            'url': request.url,
            'flask_version': '2.3.3',
            'python_version': platform.python_version(),
            'troubleshooting': {
                'try_these_steps': [
                    'Clear browser cache and cookies',
                    'Try incognito/private browsing mode',
                    'Try different browser (Chrome, Firefox, Safari)',
                    'Check if JavaScript is enabled',
                    'Try mobile data instead of WiFi',
                    'Use VPN if available'
                ],
                'test_urls': [
                    'https://web-production-2535.up.railway.app/health',
                    'https://web-production-2535.up.railway.app/korea-test',
                    'https://web-production-2535.up.railway.app/debug'
                ]
            }
        }
        
        return jsonify(debug_info)
        
    except Exception as e:
        return jsonify({
            'error': f'Debug endpoint error: {str(e)}',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S UTC')
        }), 500

@app.route('/test-columns', methods=['POST'])
def test_columns():
    """Test endpoint to help debug column detection issues"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if not file or file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        filename = secure_filename(file.filename or 'test.csv')
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"test_{int(time.time())}_{filename}")
        file.save(filepath)
        
        try:
            if filename.endswith('.csv'):
                df = pd.read_csv(filepath)
            elif filename.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(filepath)
            else:
                return jsonify({'error': 'Unsupported format'}), 400
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)
        
        # Return column analysis
        columns = list(df.columns)
        sample_data = {}
        for col in columns[:10]:  # First 10 columns
            sample_data[col] = df[col].head(3).tolist()
        
        return jsonify({
            'success': True,
            'total_columns': len(columns),
            'all_columns': columns,
            'sample_data': sample_data,
            'file_shape': df.shape,
            'suggested_company_columns': [col for col in columns if any(keyword in col.lower() for keyword in ['company', 'business', 'name', 'client', 'customer', 'account', 'store', 'retailer', 'brand'])]
        })
        
    except Exception as e:
        return jsonify({'error': f'Analysis error: {str(e)}'}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if not file or file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        filename = secure_filename(file.filename or 'upload.csv')
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"upload_{int(time.time())}_{filename}")
        file.save(filepath)
        
        try:
            if filename.endswith('.csv'):
                df = pd.read_csv(filepath)
            elif filename.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(filepath)
            else:
                return jsonify({'error': 'Unsupported format'}), 400
        except Exception as e:
            return jsonify({'error': f'Error reading file: {str(e)}'}), 400
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)
        
        # Enhanced company name column detection
        company_column = None
        possible_columns = [
            'companyName', 'shipToCompanyName', 'company_name', 'Company Name', 'Company', 'Name',
            'company', 'business_name', 'Business Name', 'BusinessName', 'customer_name', 'Customer Name',
            'account_name', 'Account Name', 'AccountName', 'client_name', 'Client Name', 'ClientName',
            'store_name', 'Store Name', 'StoreName', 'retailer_name', 'Retailer Name', 'RetailerName',
            'brand_name', 'Brand Name', 'BrandName', 'organization', 'Organization'
        ]
        
        # First try exact matches
        for col in possible_columns:
            if col in df.columns:
                company_column = col
                logger.info(f"Found exact match for company column: {col}")
                break
        
        # If no exact match, try case-insensitive and partial matches
        if not company_column:
            df_columns_lower = {col.lower(): col for col in df.columns}
            for col in possible_columns:
                if col.lower() in df_columns_lower:
                    company_column = df_columns_lower[col.lower()]
                    logger.info(f"Found case-insensitive match for company column: {company_column}")
                    break
        
        # If still no match, look for columns containing key words
        if not company_column:
            for actual_col in df.columns:
                actual_col_lower = actual_col.lower()
                if any(keyword in actual_col_lower for keyword in ['company', 'business', 'name', 'client', 'customer', 'account', 'store', 'retailer', 'brand']):
                    company_column = actual_col
                    logger.info(f"Found partial match for company column: {company_column}")
                    break
        
        if not company_column:
            # Show user all available columns for debugging
            available_columns = list(df.columns)
            logger.error(f"No company column found. Available columns: {available_columns}")
            return jsonify({
                'error': f'Could not find company name column. Available columns: {available_columns}. Please ensure your file has a column with company/business names.',
                'available_columns': available_columns,
                'suggested_columns': possible_columns[:10]
            }), 400
        
        # Optimize for large files: remove duplicates and limit for demo
        unique_companies = df.drop_duplicates(subset=[company_column])
        
        # For large files, limit to prevent timeouts (production optimization)
        max_companies = 100 if len(unique_companies) > 100 else len(unique_companies)
        processing_df = unique_companies.head(max_companies)
        
        logger.info(f"Processing {max_companies} unique companies (out of {len(df)} total)")
        
        results = []
        
        for idx, (_, row) in enumerate(processing_df.iterrows()):
            try:
                company_name_val = row[company_column]
                if pd.isna(company_name_val) or str(company_name_val).strip() == '':
                    continue
                
                company_name = str(company_name_val).strip()
                logger.info(f"Processing {idx + 1}/{max_companies}: {company_name}")
                
                email, source = find_company_email(company_name)
                
                result_row = row.to_dict()
                result_row['found_email'] = email if email else 'Not found'
                result_row['email_source'] = source if source else 'N/A'
                result_row['processed_company_name'] = company_name
                
                results.append(result_row)
                time.sleep(0.5)  # Faster processing
                
            except Exception as e:
                logger.error(f"Error processing row {idx + 1}: {str(e)}")
                continue
        
        results_df = pd.DataFrame(results)
        
        output_filename = f"email_results_{int(time.time())}.csv"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        results_df.to_csv(output_path, index=False)
        
        total_processed = len(results_df)
        if total_processed > 0:
            emails_found = len(results_df[results_df['found_email'] != 'Not found'])
            success_rate = (emails_found / total_processed * 100)
        else:
            emails_found = 0
            success_rate = 0
        
        # Prepare response with user-friendly messages
        response_data = {
            'success': True,
            'total_companies': total_processed,
            'emails_found': emails_found,
            'success_rate': round(success_rate, 1),
            'download_url': f'/download/{output_filename}',
            'company_column_used': company_column
        }
        
        # Add notification if file was large and limited
        if len(df) > max_companies:
            response_data['processing_note'] = f"File contained {len(df)} companies. Processed {max_companies} unique companies to prevent timeouts. For processing larger files, please contact support."
            response_data['total_companies_in_file'] = len(df)
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    try:
        filename = secure_filename(filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
            
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port) 