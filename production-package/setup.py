#!/usr/bin/env python3
"""
FashionGo Email Scraper - Setup Script
Automates local development environment setup
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed")
        print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python 3.11+ is available"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 11:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.11+")
        return False

def install_dependencies():
    """Install required Python packages"""
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        print("💡 Try: python3 -m pip install -r requirements.txt")
        return run_command("python3 -m pip install -r requirements.txt", "Installing dependencies (alternative)")
    return True

def test_application():
    """Test if the application starts correctly"""
    print("🧪 Testing application startup...")
    try:
        import app
        print("✅ Application imports successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def create_sample_file():
    """Create sample Excel file if it doesn't exist"""
    if not os.path.exists("sample_companies.xlsx"):
        print("📁 Creating sample companies file...")
        try:
            import pandas as pd
            companies = ["Nike", "Adidas", "Microsoft", "Apple", "Google"]
            df = pd.DataFrame({'company': companies})
            df.to_excel('sample_companies.xlsx', index=False)
            print("✅ Sample file created: sample_companies.xlsx")
        except Exception as e:
            print(f"❌ Failed to create sample file: {e}")
            return False
    else:
        print("✅ Sample file already exists")
    return True

def main():
    """Main setup function"""
    print("🚀 FashionGo Email Scraper - Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        print("\n💡 Please install Python 3.11 or higher:")
        print("   - macOS: brew install python@3.11")
        print("   - Windows: Download from python.org")
        print("   - Linux: apt install python3.11")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Failed to install dependencies")
        print("💡 Manual installation:")
        print("   pip install Flask pandas requests beautifulsoup4 openpyxl gunicorn")
        sys.exit(1)
    
    # Test application
    if not test_application():
        print("\n❌ Application test failed")
        sys.exit(1)
    
    # Create sample file
    create_sample_file()
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("   1. Run locally: python3 app.py")
    print("   2. Open browser: http://localhost:5000")
    print("   3. Test with: sample_companies.xlsx")
    print("   4. Deploy using: DEPLOYMENT_GUIDE.md")
    print("\n📖 Documentation:")
    print("   - README.md - Overview and features")
    print("   - TECHNICAL_SPECS.md - Architecture details")
    print("   - DEPLOYMENT_GUIDE.md - Deployment instructions")

if __name__ == "__main__":
    main() 