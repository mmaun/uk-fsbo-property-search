#!/bin/bash

# UK FSBO Property Search - Quick Start Script

echo "🏠 UK FSBO Property Search - Quick Start"
echo "========================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11+ first."
    exit 1
fi

echo "✅ Python 3 found"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp env.example .env
    echo "✅ Created .env file"
    echo "⚠️  Please edit .env file with your API keys before continuing"
    echo "   Required keys: OPENAI_API_KEY, TAVILY_API_KEY, PINECONE_API_KEY, PINECONE_ENVIRONMENT"
    echo
    read -p "Press Enter after you've configured your API keys..."
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Test the system
echo "🧪 Testing system..."
python3 test_system.py

if [ $? -eq 0 ]; then
    echo "✅ System test passed"
else
    echo "⚠️  System test failed. Please check your API keys and try again."
    exit 1
fi

echo
echo "🎉 Setup complete! Choose your next step:"
echo
echo "1. 🚀 Run property ingestion (scrape and index properties):"
echo "   python3 ingestion/ingest.py"
echo
echo "2. 🌐 Start the web application:"
echo "   streamlit run frontend/app.py"
echo
echo "3. 🧪 Test the RAG backend:"
echo "   python3 backend/core.py"
echo
echo "📖 For detailed instructions, see README.md"
