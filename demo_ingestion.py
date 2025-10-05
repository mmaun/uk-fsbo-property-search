#!/usr/bin/env python3
"""
Demo ingestion with sample UK FSBO property data
This allows you to test the complete system without relying on web scraping
"""

import os
from typing import List, Dict
from dotenv import load_dotenv
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

load_dotenv()

# Configuration
INDEX_NAME = os.getenv("INDEX_NAME", "uk-fsbo-properties")

# Sample UK FSBO Properties
SAMPLE_PROPERTIES = [
    {
        "title": "3 Bedroom Victorian House - Private Sale",
        "price": 285000,
        "bedrooms": 3,
        "bathrooms": 2,
        "property_type": "house",
        "location": "Manchester",
        "postcode": "M1 1AA",
        "is_fsbo": True,
        "fsbo_indicators": ["private sale", "no agent fees"],
        "source": "Gumtree",
        "url": "https://www.gumtree.com/p/property/3-bed-victorian-house-manchester",
        "description": "Beautiful Victorian house in Manchester city centre. Private sale - no estate agent fees! 3 bedrooms, 2 bathrooms, period features throughout. Close to transport links and amenities. Direct from owner - save thousands on agent fees!"
    },
    {
        "title": "2 Bed Flat - Owner Direct Sale",
        "price": 195000,
        "bedrooms": 2,
        "bathrooms": 1,
        "property_type": "flat",
        "location": "Birmingham",
        "postcode": "B1 1AA",
        "is_fsbo": True,
        "fsbo_indicators": ["owner direct", "no commission"],
        "source": "TheHouseShop",
        "url": "https://www.thehouseshop.com/property/2-bed-flat-birmingham",
        "description": "Modern 2-bedroom flat in Birmingham. Owner selling directly - no estate agent commission! Recently refurbished, modern kitchen, close to city centre. Perfect for first-time buyers or investors."
    },
    {
        "title": "4 Bed Detached House - FSBO",
        "price": 425000,
        "bedrooms": 4,
        "bathrooms": 3,
        "property_type": "house",
        "location": "Leeds",
        "postcode": "LS1 1AA",
        "is_fsbo": True,
        "fsbo_indicators": ["fsbo", "private seller"],
        "source": "PropertyHeads",
        "url": "https://www.propertyheads.co.uk/property/4-bed-detached-leeds",
        "description": "Spacious 4-bedroom detached house in Leeds. For Sale By Owner - no agent fees! Large garden, garage, modern kitchen. Family home in quiet residential area. Direct negotiation with owner."
    },
    {
        "title": "1 Bed Studio Apartment",
        "price": 125000,
        "bedrooms": 1,
        "bathrooms": 1,
        "property_type": "studio",
        "location": "Liverpool",
        "postcode": "L1 1AA",
        "is_fsbo": False,
        "fsbo_indicators": [],
        "source": "OnTheMarket",
        "url": "https://www.onthemarket.com/property/1-bed-studio-liverpool",
        "description": "Modern studio apartment in Liverpool city centre. Perfect for young professionals. Open plan living, modern fixtures, close to transport links."
    },
    {
        "title": "3 Bed Semi-Detached - Private Sale",
        "price": 275000,
        "bedrooms": 3,
        "bathrooms": 2,
        "property_type": "house",
        "location": "Bristol",
        "postcode": "BS1 1AA",
        "is_fsbo": True,
        "fsbo_indicators": ["private sale", "no agent"],
        "source": "PropertyMutual",
        "url": "https://www.propertymutual.co.uk/property/3-bed-semi-bristol",
        "description": "Charming 3-bedroom semi-detached house in Bristol. Private sale - no estate agent involved! Period features, large garden, off-street parking. Direct from owner."
    },
    {
        "title": "2 Bed Terraced House",
        "price": 185000,
        "bedrooms": 2,
        "bathrooms": 1,
        "property_type": "house",
        "location": "Newcastle",
        "postcode": "NE1 1AA",
        "is_fsbo": True,
        "fsbo_indicators": ["direct from owner", "save on fees"],
        "source": "OpenRent",
        "url": "https://www.openrent.com/property/2-bed-terraced-newcastle",
        "description": "Traditional 2-bedroom terraced house in Newcastle. Owner selling directly - save on estate agent fees! Recently updated, close to city centre, good transport links."
    },
    {
        "title": "5 Bed Family Home - No Agent Fees",
        "price": 550000,
        "bedrooms": 5,
        "bathrooms": 4,
        "property_type": "house",
        "location": "Edinburgh",
        "postcode": "EH1 1AA",
        "is_fsbo": True,
        "fsbo_indicators": ["no agent fees", "private sale"],
        "source": "Houser",
        "url": "https://www.houser.com/property/5-bed-family-edinburgh",
        "description": "Luxurious 5-bedroom family home in Edinburgh. Private sale with no estate agent fees! Large garden, double garage, modern kitchen. Perfect for growing families."
    },
    {
        "title": "1 Bed Apartment - City Centre",
        "price": 165000,
        "bedrooms": 1,
        "bathrooms": 1,
        "property_type": "flat",
        "location": "Cardiff",
        "postcode": "CF1 1AA",
        "is_fsbo": False,
        "fsbo_indicators": [],
        "source": "Home.co.uk",
        "url": "https://www.home.co.uk/property/1-bed-apartment-cardiff",
        "description": "Modern 1-bedroom apartment in Cardiff city centre. High-spec finish, balcony, secure parking. Ideal for professionals or investors."
    }
]


class ReducedDimensionEmbeddings(OpenAIEmbeddings):
    """
    Custom embeddings class that reduces 1536 dimensions to 1024 for Pinecone compatibility.
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed documents and reduce dimensions."""
        embeddings = super().embed_documents(texts)
        return [self._reduce_dimensions(emb) for emb in embeddings]
    
    def embed_query(self, text: str) -> List[float]:
        """Embed query and reduce dimensions."""
        embedding = super().embed_query(text)
        return self._reduce_dimensions(embedding)
    
    def _reduce_dimensions(self, embedding: List[float]) -> List[float]:
        """Reduce embedding dimensions from 1536 to 1024."""
        if len(embedding) == 1536:
            # Use intelligent sampling to preserve important features
            # Take every 1.5th element (1536/1024 = 1.5)
            step = 1536 / 1024
            indices = [int(i * step) for i in range(1024)]
            return [embedding[i] for i in indices]
        return embedding


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
{prop['description']}

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
    
    # Initialize embeddings with dimension reduction
    embeddings = ReducedDimensionEmbeddings(model="text-embedding-3-small")
    
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


def main():
    """
    Main demo ingestion pipeline.
    """
    print("="*60)
    print("UK FSBO PROPERTY SEARCH - DEMO INGESTION")
    print("="*60)
    
    # Step 1: Use sample properties
    properties = SAMPLE_PROPERTIES
    print(f"\n📄 Using {len(properties)} sample properties")
    
    # Step 2: Convert to LangChain documents
    print("\n📄 Creating LangChain documents...")
    documents = create_langchain_documents(properties)
    print(f"   Created {len(documents)} documents")
    
    # Step 3: Index to Pinecone
    index_to_pinecone(documents)
    
    print("\n" + "="*60)
    print("✅ DEMO INGESTION COMPLETE!")
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
    main()
