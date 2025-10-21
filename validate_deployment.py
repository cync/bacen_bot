#!/usr/bin/env python3
"""
Deployment test script - validates configuration before Railway deployment
"""
import os
import sys
from dotenv import load_dotenv

def validate_environment():
    """Validate all required environment variables are set"""
    print("🔍 Validating environment configuration...")
    
    # Load environment variables
    load_dotenv()
    
    required_vars = {
        "DATABASE_URL": "PostgreSQL connection string",
        "TELEGRAM_TOKEN": "Telegram bot token from @BotFather"
    }
    
    optional_vars = {
        "MAX_ITEMS_PER_FEED": "Maximum items to process per feed (default: 50)"
    }
    
    missing_vars = []
    
    # Check required variables
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value:
            missing_vars.append(f"❌ {var}: {description}")
        else:
            print(f"✅ {var}: Set")
    
    # Check optional variables
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value}")
        else:
            print(f"ℹ️  {var}: Not set (will use default)")
    
    if missing_vars:
        print("\n❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   {var}")
        print("\nPlease set these variables in your Railway project settings")
        return False
    
    print("\n✅ All required environment variables are set!")
    return True

def test_imports():
    """Test that all required modules can be imported"""
    print("\n🔍 Testing module imports...")
    
    try:
        import asyncio
        print("✅ asyncio")
        
        import psycopg2
        print("✅ psycopg2")
        
        import feedparser
        print("✅ feedparser")
        
        from bs4 import BeautifulSoup
        print("✅ beautifulsoup4")
        
        from aiogram import Bot, Dispatcher
        print("✅ aiogram")
        
        from pydantic import BaseModel
        print("✅ pydantic")
        
        from dotenv import load_dotenv
        print("✅ python-dotenv")
        
        print("\n✅ All required modules imported successfully!")
        return True
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("Please install missing dependencies with: pip install -r requirements.txt")
        return False

def main():
    """Main validation function"""
    print("🚀 BACEN Bot Deployment Validation")
    print("=" * 40)
    
    # Test imports first
    if not test_imports():
        sys.exit(1)
    
    # Validate environment
    if not validate_environment():
        sys.exit(1)
    
    print("\n🎉 Deployment validation passed!")
    print("Your bot is ready to be deployed to Railway!")
    print("\nNext steps:")
    print("1. Push your code to GitHub")
    print("2. Connect your repository to Railway")
    print("3. Set the environment variables in Railway")
    print("4. Deploy!")

if __name__ == "__main__":
    main()
