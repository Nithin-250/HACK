#!/usr/bin/env python3
"""
Simple run script for Financial Fraud Detection System
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if all requirements are met"""
    # Check if .env file exists
    if not Path('.env').exists():
        print("❌ .env file not found. Run setup.py first!")
        return False
    
    # Check if static directory exists
    if not Path('static').exists():
        print("❌ Static directory not found. Run setup.py first!")
        return False
    
    # Check if main.py exists
    if not Path('main.py').exists():
        print("❌ main.py not found!")
        return False
    
    return True

def start_application():
    """Start the FastAPI application"""
    print("🚀 Starting Financial Fraud Detection System...")
    print("=" * 50)
    
    try:
        # Import and run the application
        import uvicorn
        from main import app
        
        print("✅ Application starting on http://localhost:8000")
        print("🌐 Web interface: http://localhost:8000/app")
        print("📖 API docs: http://localhost:8000/docs")
        print("\n⚠️  Make sure MongoDB is running!")
        print("💡 Press Ctrl+C to stop the application")
        print("=" * 50)
        
        # Start the server
        uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Try running: python setup.py")
        return False
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
        return True
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        return False

def main():
    """Main function"""
    if not check_requirements():
        print("\n💡 Run 'python setup.py' to set up the application first")
        sys.exit(1)
    
    start_application()

if __name__ == "__main__":
    main()