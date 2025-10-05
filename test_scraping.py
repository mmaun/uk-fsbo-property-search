#!/usr/bin/env python3
"""
Test Tavily scraping with a single website
"""

import asyncio
import os
from dotenv import load_dotenv
from langchain_tavily import TavilyMap, TavilyExtract

# Load environment variables
load_dotenv()

async def test_single_website():
    """Test scraping a single website."""
    
    # Test with a simple website first
    test_url = "https://www.gumtree.com/for-sale/property"
    
    print(f"🔍 Testing Tavily scraping with: {test_url}")
    
    # Step 1: Map the website
    print("\n1. Mapping website...")
    map_tool = TavilyMap(
        max_depth=1,
        max_breadth=5,
        limit=10,
        tavily_api_key=os.getenv("TAVILY_API_KEY")
    )
    
    try:
        sitemap = map_tool.invoke({"url": test_url})
        print(f"   Raw sitemap type: {type(sitemap)}")
        print(f"   Raw sitemap: {sitemap}")
        
        # Process the sitemap
        if isinstance(sitemap, list):
            valid_urls = [url for url in sitemap if isinstance(url, str) and url.startswith('http')]
            print(f"   Valid URLs found: {len(valid_urls)}")
            for i, url in enumerate(valid_urls[:3]):  # Show first 3
                print(f"   {i+1}. {url}")
        else:
            print(f"   Sitemap is not a list: {type(sitemap)}")
            return
            
    except Exception as e:
        print(f"   ❌ Map failed: {e}")
        return
    
    # Step 2: Extract content from first few URLs
    if valid_urls:
        print(f"\n2. Extracting content from first URL...")
        extract_tool = TavilyExtract(tavily_api_key=os.getenv("TAVILY_API_KEY"))
        
        try:
            result = await extract_tool.ainvoke({"urls": [valid_urls[0]]})
            print(f"   Extract result type: {type(result)}")
            print(f"   Extract result keys: {result.keys() if isinstance(result, dict) else 'Not a dict'}")
            
            if isinstance(result, dict) and "results" in result:
                documents = result["results"]
                print(f"   Documents found: {len(documents)}")
                
                if documents:
                    doc = documents[0]
                    print(f"   First document keys: {doc.keys() if isinstance(doc, dict) else 'Not a dict'}")
                    if isinstance(doc, dict):
                        print(f"   URL: {doc.get('url', 'N/A')}")
                        print(f"   Title: {doc.get('title', 'N/A')}")
                        print(f"   Content preview: {str(doc.get('raw_content', ''))[:200]}...")
            
        except Exception as e:
            print(f"   ❌ Extract failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_single_website())
