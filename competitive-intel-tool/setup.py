#!/usr/bin/env python3
"""
Setup script for Personal Competitive Intelligence Tool
Run this to install dependencies and get started
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All packages installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False

def create_config_file():
    """Create a sample config file"""
    config_content = """
# Personal CI Tool Configuration
# Copy this file to config.py and add your API keys

# OpenAI API Key (required)
# Get your API key from: https://platform.openai.com/api-keys
OPENAI_API_KEY = "sk-your-openai-api-key-here"

# Google Custom Search API Key (optional - for better competitor discovery)
# Get your API key from: https://console.developers.google.com/
GOOGLE_API_KEY = "your-google-api-key-here"
GOOGLE_CSE_ID = "your-custom-search-engine-id"

# SerpAPI Key (optional - for enhanced search results)
# Get your API key from: https://serpapi.com/
SERPAPI_KEY = "your-serpapi-key-here"
"""
    
    with open("config_sample.py", "w") as f:
        f.write(config_content)
    
    print("📝 Created config_sample.py - copy to config.py and add your API keys")

def main():
    print("🧠 Personal Competitive Intelligence Tool Setup")
    print("=" * 50)
    
    # Install requirements
    if not install_requirements():
        print("❌ Setup failed. Please check the error messages above.")
        return
    
    # Create config file
    create_config_file()
    
    print("\n🚀 Setup Complete!")
    print("\nNext steps:")
    print("1. Copy config_sample.py to config.py")
    print("2. Add your OpenAI API key to config.py")
    print("3. Run: streamlit run main.py")
    print("\n💡 Get your OpenAI API key from: https://platform.openai.com/api-keys")
    print("💰 Expected monthly cost: $5-15 (depending on usage)")

if __name__ == "__main__":
    main()
