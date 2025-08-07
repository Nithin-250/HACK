#!/usr/bin/env python3
"""
Setup script for Financial Fraud Detection System
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version}")

def check_mongodb():
    """Check if MongoDB is available"""
    try:
        result = subprocess.run(['mongod', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ MongoDB is installed")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    print("⚠️  MongoDB not found. Please install MongoDB:")
    print("   - Download from: https://www.mongodb.com/try/download/community")
    print("   - Or use MongoDB Atlas (cloud): https://www.mongodb.com/atlas")
    return False

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_environment():
    """Setup environment configuration"""
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    if not env_file.exists():
        if env_example.exists():
            shutil.copy(env_example, env_file)
            print("✅ Created .env file from template")
            print("📝 Please edit .env file with your configuration")
        else:
            # Create basic .env file
            with open(env_file, 'w') as f:
                f.write("MONGO_URI=mongodb://localhost:27017\n")
                f.write("DB_NAME=fraud_detection\n")
                f.write("SECRET_KEY=change-this-secret-key-in-production\n")
            print("✅ Created basic .env file")
    else:
        print("✅ .env file already exists")

def create_directories():
    """Create necessary directories"""
    static_dir = Path('static')
    if not static_dir.exists():
        static_dir.mkdir()
        print("✅ Created static directory")
    else:
        print("✅ Static directory exists")

def run_tests():
    """Run basic tests to verify installation"""
    print("🧪 Running basic tests...")
    try:
        # Test imports
        import fastapi
        import pymongo
        import bcrypt
        import jwt
        import geopy
        import numpy
        import scipy
        print("✅ All required packages imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "="*50)
    print("🎉 Setup completed successfully!")
    print("="*50)
    print("\nNext steps:")
    print("1. Make sure MongoDB is running:")
    print("   mongod")
    print("\n2. Start the application:")
    print("   python main.py")
    print("\n3. Open your browser and go to:")
    print("   http://localhost:8000/app")
    print("\n4. Create an account and start detecting fraud!")
    print("\n📚 For more information, see README.md")

def main():
    """Main setup function"""
    print("🚀 Setting up Financial Fraud Detection System")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Check MongoDB
    mongodb_available = check_mongodb()
    
    # Create directories
    create_directories()
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Setup environment
    setup_environment()
    
    # Run tests
    if not run_tests():
        sys.exit(1)
    
    # Print next steps
    print_next_steps()
    
    if not mongodb_available:
        print("\n⚠️  Remember to install and start MongoDB before running the application!")

if __name__ == "__main__":
    main()