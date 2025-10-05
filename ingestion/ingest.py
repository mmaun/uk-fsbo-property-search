"""
UK FSBO Property Ingestion Pipeline
Uses Tavily for web scraping and Pinecone for vector storage
"""

import os
import asyncio
import re
from typing import List, Dict, Tuple
from dotenv import load_dotenv
from langchain_tavily import TavilyMap, TavilyExtract
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

load_dotenv()

# Configuration
INDEX_NAME = os.getenv("INDEX_NAME", "uk-fsbo-properties")

# UK Property Sources
PROPERTY_SOURCES = [
    "https://www.gumtree.com/for-sale/property",
    "https://www.thehouseshop.com/",
    "https://www.openrent.com/",
    "https://www.nethouseprices.com/",
    "https://www.home.co.uk/",
    "https://www.propertyheads.co.uk/",
    "https://www.propertymutual.co.uk/",
    "https://www.propertyadvertiser.co.uk/",
    "https://www.houser.com/",
    "https://www.onthemarket.com/",
    # Note: Facebook Marketplace requires special handling
]

# FSBO Detection Keywords
FSBO_KEYWORDS = [
    "private sale", "no agent", "no estate agent", "owner selling",
    "direct from owner", "fsbo", "for sale by owner", "private seller",
    "no commission", "save on fees", "owner sale", "private vendor",
    "no agent fees", "direct sale", "owner direct", "private listing"
]

# UK Cities for location detection
UK_CITIES = [
    "London", "Manchester", "Birmingham", "Leeds", "Liverpool", 
    "Glasgow", "Edinburgh", "Bristol", "Cardiff", "Belfast",
    "Newcastle", "Sheffield", "Nottingham", "Leicester", "Coventry",
    "Bradford", "Hull", "Plymouth", "Stoke", "Wolverhampton",
    "Derby", "Southampton", "Portsmouth", "Brighton", "Preston",
    "Swansea", "Middlesbrough", "Sunderland", "Norwich", "Walsall"
]


def detect_fsbo(content: str, title: str = "") -> Tuple[bool, List[str]]:
    """
    Detect if a property is FSBO based on content.
    
    Args:
        content: Property description content
        title: Property title/heading
        
    Returns:
        (is_fsbo, matching_keywords)
    """
    text = (content + " " + title).lower()
    matches = [kw for kw in FSBO_KEYWORDS if kw in text]
    return len(matches) > 0, matches


def extract_source_from_url(url: str) -> str:
    """Extract website name from URL."""
    if "gumtree" in url:
        return "Gumtree"
    elif "thehouseshop" in url:
        return "TheHouseShop"
    elif "openrent" in url:
        return "OpenRent"
    elif "nethouseprices" in url:
        return "NetHousePrices"
    elif "home.co.uk" in url:
        return "Home.co.uk"
    elif "propertyheads" in url:
        return "PropertyHeads"
    elif "propertymutual" in url:
        return "PropertyMutual"
    elif "propertyadvertiser" in url:
        return "PropertyAdvertiser"
    elif "houser" in url:
        return "Houser"
    elif "onthemarket" in url:
        return "OnTheMarket"
    elif "facebook" in url:
        return "Facebook Marketplace"
    return "Unknown"


def extract_price(content: str) -> int:
    """Extract price from content using regex patterns."""
    # Look for £XXX,XXX or £XXX.XXX patterns
    price_patterns = [
        r'£([\d,]+)',
        r'£([\d.]+)',
        r'(\d+)\s*(?:pounds|GBP)',
        r'(\d+)\s*£',
    ]
    
    for pattern in price_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            try:
                # Clean the price string
                price_str = match.replace(',', '').replace('.', '')
                price = int(price_str)
                # Reasonable price range for UK properties
                if 10000 <= price <= 10000000:
                    return price
            except ValueError:
                continue
    return 0


def extract_bedrooms(content: str) -> int:
    """Extract number of bedrooms."""
    patterns = [
        r'(\d+)\s*bed',
        r'(\d+)\s*bedroom',
        r'(\d+)\s*br',
    ]
    for pattern in patterns:
        match = re.search(pattern, content.lower())
        if match:
            try:
                beds = int(match.group(1))
                if 1 <= beds <= 10:  # Reasonable range
                    return beds
            except ValueError:
                continue
    return 0


def extract_bathrooms(content: str) -> int:
    """Extract number of bathrooms."""
    patterns = [
        r'(\d+)\s*bath',
        r'(\d+)\s*bathroom',
        r'(\d+)\s*ba',
    ]
    for pattern in patterns:
        match = re.search(pattern, content.lower())
        if match:
            try:
                baths = int(match.group(1))
                if 1 <= baths <= 10:  # Reasonable range
                    return baths
            except ValueError:
                continue
    return 0


def extract_property_type(content: str) -> str:
    """Detect property type."""
    content_lower = content.lower()
    if any(word in content_lower for word in ["flat", "apartment"]):
        return "flat"
    elif "house" in content_lower:
        return "house"
    elif "bungalow" in content_lower:
        return "bungalow"
    elif "cottage" in content_lower:
        return "cottage"
    elif "studio" in content_lower:
        return "studio"
    elif "maisonette" in content_lower:
        return "maisonette"
    return "unknown"


def extract_location(content: str) -> str:
    """Extract location/city from content."""
    content_lower = content.lower()
    for city in UK_CITIES:
        if city.lower() in content_lower:
            return city
    return "Unknown"


def extract_postcode(content: str) -> str:
    """Extract UK postcode."""
    # UK postcode pattern
    pattern = r'[A-Z]{1,2}\d{1,2}\s?\d[A-Z]{2}'
    match = re.search(pattern, content.upper())
    return match.group(0) if match else ""


def extract_property_details(doc: Dict) -> Dict:
    """
    Extract structured property data from scraped content.
    """
    content = doc.get("raw_content", "")
    url = doc.get("url", "")
    title = doc.get("title", "")
    
    # Initialize property data
    property_data = {
        "url": url,
        "title": title,
        "source": extract_source_from_url(url),
        "raw_content": content,
        "price": extract_price(content + " " + title),
        "bedrooms": extract_bedrooms(content + " " + title),
        "bathrooms": extract_bathrooms(content + " " + title),
        "property_type": extract_property_type(content + " " + title),
        "location": extract_location(content + " " + title),
        "postcode": extract_postcode(content + " " + title),
        "description": content[:1000],  # First 1000 chars
    }
    
    # Detect FSBO
    is_fsbo, fsbo_keywords = detect_fsbo(content, title)
    property_data["is_fsbo"] = is_fsbo
    property_data["fsbo_indicators"] = fsbo_keywords
    
    return property_data


def chunk_urls(urls: List[str], chunk_size: int = 10) -> List[List[str]]:
    """Split URLs into batches for concurrent processing."""
    return [urls[i:i + chunk_size] for i in range(0, len(urls), chunk_size)]


async def scrape_property_source(base_url: str) -> List[Dict]:
    """
    Scrape a single property website using Tavily.
    
    Steps:
    1. Use TavilyMap to discover all listing URLs
    2. Use TavilyExtract to get content from each listing
    3. Return structured property data
    """
    print(f"\n🔍 Scraping: {base_url}")
    
    # Step 1: Map the website to discover listing URLs
    map_tool = TavilyMap(
        max_depth=2,        # Don't go too deep
        max_breadth=15,     # Follow up to 15 links per page
        limit=50            # Max 50 URLs per source (adjust as needed)
    )
    
    try:
        sitemap = map_tool.invoke({"url": base_url})
        print(f"   Discovered {len(sitemap)} URLs")
    except Exception as e:
        print(f"   ❌ Map failed: {e}")
        return []
    
    # Step 2: Extract content from URLs in batches
    extract_tool = TavilyExtract()
    all_properties = []
    
    url_batches = chunk_urls(sitemap, chunk_size=5)  # Smaller batches for stability
    
    for i, batch in enumerate(url_batches, 1):
        print(f"   Processing batch {i}/{len(url_batches)} ({len(batch)} URLs)")
        
        try:
            result = await extract_tool.ainvoke({"urls": batch})
            documents = result.get("results", [])
            
            # Process each document
            for doc in documents:
                property_data = extract_property_details(doc)
                
                # Only keep if we could extract meaningful data
                if (property_data["price"] > 0 or 
                    property_data["bedrooms"] > 0 or 
                    property_data["location"] != "Unknown"):
                    all_properties.append(property_data)
            
            print(f"   ✅ Extracted {len(documents)} properties from batch {i}")
            
        except Exception as e:
            print(f"   ⚠️  Batch {i} failed: {e}")
            continue
    
    print(f"   Total properties from {base_url}: {len(all_properties)}")
    return all_properties


async def scrape_all_sources() -> List[Dict]:
    """
    Scrape all property sources concurrently.
    """
    print("🚀 Starting scrape of all property sources...\n")
    
    # Create tasks for concurrent scraping
    tasks = [scrape_property_source(url) for url in PROPERTY_SOURCES]
    
    # Run all scrapes concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Flatten results
    all_properties = []
    for i, result in enumerate(results):
        if isinstance(result, list):
            all_properties.extend(result)
        else:
            print(f"⚠️  Source {PROPERTY_SOURCES[i]} failed: {result}")
    
    print(f"\n✅ Total properties scraped: {len(all_properties)}")
    print(f"   FSBO properties: {sum(1 for p in all_properties if p['is_fsbo'])}")
    
    return all_properties


def create_langchain_documents(properties: List[Dict]) -> List[Document]:
    """
    Convert property data into LangChain Document objects.
    """
    documents = []
    
    for prop in properties:
        # Create content string
        content = f"""
Property Listing:
Source: {prop['source']}
Title: {prop['title']}
Price: £{prop['price']:,}
Location: {prop['location']}
Bedrooms: {prop['bedrooms']}
Bathrooms: {prop['bathrooms']}
Type: {prop['property_type']}
FSBO: {'Yes' if prop['is_fsbo'] else 'No'}
Postcode: {prop['postcode']}

Description:
{prop['raw_content'][:1500]}

Listing URL: {prop['url']}
"""
        
        # Create metadata
        metadata = {
            "source": prop['source'],
            "url": prop['url'],
            "title": prop['title'],
            "price": prop['price'],
            "location": prop['location'],
            "postcode": prop['postcode'],
            "bedrooms": prop['bedrooms'],
            "bathrooms": prop['bathrooms'],
            "property_type": prop['property_type'],
            "is_fsbo": prop['is_fsbo'],
            "fsbo_indicators": ",".join(prop.get('fsbo_indicators', [])),
        }
        
        # Create Document
        doc = Document(
            page_content=content,
            metadata=metadata
        )
        documents.append(doc)
    
    return documents


def index_to_pinecone(documents: List[Document]):
    """
    Index documents to Pinecone vector database.
    """
    print(f"\n📊 Indexing {len(documents)} properties to Pinecone...")
    
    # Initialize embeddings
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    # Chunk documents if needed (properties are usually short, but just in case)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )
    
    split_docs = text_splitter.split_documents(documents)
    print(f"   Split into {len(split_docs)} chunks")
    
    # Index to Pinecone
    PineconeVectorStore.from_documents(
        documents=split_docs,
        embedding=embeddings,
        index_name=INDEX_NAME
    )
    
    print("   ✅ Indexing complete!")


async def main():
    """
    Main ingestion pipeline.
    """
    print("="*60)
    print("UK FSBO PROPERTY INGESTION PIPELINE")
    print("="*60)
    
    # Step 1: Scrape all property sources
    properties = await scrape_all_sources()
    
    if not properties:
        print("\n❌ No properties scraped. Exiting.")
        return
    
    # Step 2: Convert to LangChain documents
    print("\n📄 Creating LangChain documents...")
    documents = create_langchain_documents(properties)
    print(f"   Created {len(documents)} documents")
    
    # Step 3: Index to Pinecone
    index_to_pinecone(documents)
    
    print("\n" + "="*60)
    print("✅ INGESTION COMPLETE!")
    print("="*60)
    print(f"Total properties: {len(properties)}")
    print(f"FSBO properties: {sum(1 for p in properties if p['is_fsbo'])}")
    print(f"Sources covered: {len(set(p['source'] for p in properties))}")
    
    # Print summary by source
    print("\n📊 Summary by Source:")
    source_counts = {}
    for prop in properties:
        source = prop['source']
        if source not in source_counts:
            source_counts[source] = {'total': 0, 'fsbo': 0}
        source_counts[source]['total'] += 1
        if prop['is_fsbo']:
            source_counts[source]['fsbo'] += 1
    
    for source, counts in source_counts.items():
        print(f"   {source}: {counts['total']} total, {counts['fsbo']} FSBO")


if __name__ == "__main__":
    asyncio.run(main())
