#!/usr/bin/env python3
"""
UK FSBO Property Search - System Test
Tests the complete system functionality
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_environment():
    """Test environment configuration."""
    print("🔧 Testing environment configuration...")
    
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
        print(f"❌ Missing API keys: {', '.join(missing_keys)}")
        return False
    
    print("✅ Environment configuration OK")
    return True

def test_imports():
    """Test if all required modules can be imported."""
    print("📦 Testing imports...")
    
    try:
        import langchain
        import langchain_openai
        import langchain_pinecone
        import langchain_tavily
        import streamlit
        import pinecone
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_rag_backend():
    """Test RAG backend functionality."""
    print("🤖 Testing RAG backend...")
    
    try:
        from backend.core import run_llm, get_property_search_prompt
        
        # Test prompt creation
        prompt = get_property_search_prompt()
        print("✅ Property search prompt created")
        
        # Test RAG function (without actually running it)
        print("✅ RAG functions imported successfully")
        return True
        
    except Exception as e:
        print(f"❌ RAG backend error: {e}")
        return False

def test_ingestion():
    """Test ingestion pipeline."""
    print("📥 Testing ingestion pipeline...")
    
    try:
        from ingestion.ingest import (
            detect_fsbo, 
            extract_price, 
            extract_bedrooms,
            extract_property_type,
            PROPERTY_SOURCES,
            FSBO_KEYWORDS
        )
        
        # Test FSBO detection
        test_content = "This is a private sale with no agent fees"
        is_fsbo, keywords = detect_fsbo(test_content)
        print(f"✅ FSBO detection: {is_fsbo} (keywords: {keywords})")
        
        # Test price extraction
        test_price = "£250,000"
        price = extract_price(test_price)
        print(f"✅ Price extraction: £{price:,}")
        
        # Test bedroom extraction
        test_beds = "3 bedroom house"
        beds = extract_bedrooms(test_beds)
        print(f"✅ Bedroom extraction: {beds}")
        
        # Test property type
        test_type = "beautiful house for sale"
        prop_type = extract_property_type(test_type)
        print(f"✅ Property type: {prop_type}")
        
        print(f"✅ Ingestion pipeline OK ({len(PROPERTY_SOURCES)} sources, {len(FSBO_KEYWORDS)} FSBO keywords)")
        return True
        
    except Exception as e:
        print(f"❌ Ingestion error: {e}")
        return False

def test_frontend():
    """Test frontend components."""
    print("🌐 Testing frontend...")
    
    try:
        import streamlit as st
        print("✅ Streamlit imported successfully")
        
        # Test if frontend app can be imported
        sys.path.append(os.path.join(os.path.dirname(__file__), 'frontend'))
        print("✅ Frontend path configured")
        
        return True
        
    except Exception as e:
        print(f"❌ Frontend error: {e}")
        return False

def test_pinecone_connection():
    """Test Pinecone connection."""
    print("🗄️ Testing Pinecone connection...")
    
    try:
        import pinecone
        
        # Initialize Pinecone
        pinecone.init(
            api_key=os.getenv("PINECONE_API_KEY"),
            environment=os.getenv("PINECONE_ENVIRONMENT")
        )
        
        # List indexes
        indexes = pinecone.list_indexes()
        print(f"✅ Pinecone connected. Available indexes: {[idx.name for idx in indexes]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Pinecone connection error: {e}")
        return False

def test_openai_connection():
    """Test OpenAI connection."""
    print("🧠 Testing OpenAI connection...")
    
    try:
        from langchain_openai import OpenAIEmbeddings
        
        # Test embeddings
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        test_embedding = embeddings.embed_query("test query")
        
        print(f"✅ OpenAI embeddings working (dimension: {len(test_embedding)})")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI connection error: {e}")
        return False

def main():
    """Run all tests."""
    print("="*60)
    print("🧪 UK FSBO Property Search - System Test")
    print("="*60)
    print()
    
    tests = [
        ("Environment", test_environment),
        ("Imports", test_imports),
        ("RAG Backend", test_rag_backend),
        ("Ingestion", test_ingestion),
        ("Frontend", test_frontend),
        ("Pinecone", test_pinecone_connection),
        ("OpenAI", test_openai_connection),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    print("\n" + "="*60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    print("="*60)
    
    if passed == total:
        print("🎉 All tests passed! System is ready to use.")
        print("\nNext steps:")
        print("1. Run: python ingestion/ingest.py")
        print("2. Run: streamlit run frontend/app.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("Make sure your API keys are configured correctly in .env")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
