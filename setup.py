#!/usr/bin/env python3
"""
UK FSBO Property Search - Setup Script
Helps users configure the system quickly
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header():
    """Print setup header."""
    print("="*60)
    print("🏠 UK FSBO Property Search - Setup Script")
    print("="*60)
    print()

def check_python_version():
    """Check if Python version is compatible."""
    print("🐍 Checking Python version...")
    if sys.version_info < (3, 11):
        print("❌ Python 3.11+ is required. Current version:", sys.version)
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def install_dependencies():
    """Install required dependencies."""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_environment():
    """Set up environment variables."""
    print("\n🔧 Setting up environment variables...")
    
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if not env_example.exists():
        print("❌ env.example file not found")
        return False
    
    # Copy example to .env
    with open(env_example, 'r') as f:
        content = f.read()
    
    with open(env_file, 'w') as f:
        f.write(content)
    
    print("✅ Created .env file from template")
    print("⚠️  Please edit .env file with your API keys:")
    print("   - OPENAI_API_KEY")
    print("   - TAVILY_API_KEY") 
    print("   - PINECONE_API_KEY")
    print("   - PINECONE_ENVIRONMENT")
    
    return True

def check_api_keys():
    """Check if API keys are configured."""
    print("\n🔑 Checking API keys...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    required_keys = [
        "OPENAI_API_KEY",
        "TAVILY_API_KEY", 
        "PINECONE_API_KEY",
        "PINECONE_ENVIRONMENT"
    ]
    
    missing_keys = []
    for key in required_keys:
        if not os.getenv(key) or os.getenv(key) == f"your_{key.lower()}_here":
            missing_keys.append(key)
    
    if missing_keys:
        print("❌ Missing or incomplete API keys:")
        for key in missing_keys:
            print(f"   - {key}")
        print("\nPlease edit .env file with your actual API keys")
        return False
    
    print("✅ All API keys configured")
    return True

def test_imports():
    """Test if all required modules can be imported."""
    print("\n🧪 Testing imports...")
    
    try:
        import langchain
        import langchain_openai
        import langchain_pinecone
        import langchain_tavily
        import streamlit
        import pinecone
        print("✅ All required modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def create_directories():
    """Create necessary directories."""
    print("\n📁 Creating directories...")
    
    directories = ["ingestion", "frontend", "backend"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created {directory}/ directory")
    
    return True

def print_next_steps():
    """Print next steps for the user."""
    print("\n" + "="*60)
    print("🎉 Setup Complete!")
    print("="*60)
    print()
    print("Next steps:")
    print("1. 🔑 Edit .env file with your API keys")
    print("2. 🚀 Run property ingestion:")
    print("   python ingestion/ingest.py")
    print("3. 🌐 Start the web app:")
    print("   streamlit run frontend/app.py")
    print("4. 🧪 Test the RAG system:")
    print("   python backend/core.py")
    print()
    print("📖 For detailed instructions, see README.md")
    print("="*60)

def main():
    """Main setup function."""
    print_header()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Test imports
    if not test_imports():
        sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        sys.exit(1)
    
    # Check API keys (optional - user can configure later)
    check_api_keys()
    
    # Print next steps
    print_next_steps()

if __name__ == "__main__":
    main()
