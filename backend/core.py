"""
UK FSBO Property Search - RAG Implementation
Preserves the RAG architecture while adapting for property search
"""

import os
from typing import Dict, List, Optional
from dotenv import load_dotenv
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_pinecone import PineconeVectorStore
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
import numpy as np

load_dotenv()

# Configuration
INDEX_NAME = os.getenv("INDEX_NAME", "uk-fsbo-properties")
EMBEDDING_MODEL = "text-embedding-3-small"
LLM_MODEL = "gpt-4-turbo"


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


def get_property_search_prompt():
    """
    Custom prompt template for UK FSBO property search.
    """
    template = """You are a UK property search assistant specializing in FSBO (For Sale By Owner) listings.

Your role is to help users find properties being sold directly by owners, without estate agents.

Answer the user's property search query based SOLELY on the property listings in the context below.

GUIDELINES:
1. **Focus on FSBO**: Prioritize properties marked as FSBO (For Sale By Owner)
2. **Be Specific**: Provide price, location, bedrooms, bathrooms, and key features
3. **Cite Sources**: Always mention the source website (Gumtree, OpenRent, etc.) and include the listing URL
4. **Compare Options**: If multiple properties match, compare them and highlight the best options
5. **Highlight Value**: Mention FSBO benefits like "no agent fees" or "direct negotiation with owner"
6. **UK Format**: Use British pounds (£) and property terminology (flat not apartment, postcode not zip)
7. **Be Honest**: If no properties match the criteria exactly, say so and suggest alternatives

CONTEXT (Property Listings):
{context}

USER QUESTION:
{input}

ASSISTANT RESPONSE (be helpful and specific):
"""
    
    return ChatPromptTemplate.from_template(template)


def run_llm(
    query: str,
    price_max: Optional[int] = None,
    price_min: Optional[int] = None,
    bedrooms: Optional[int] = None,
    location: Optional[str] = None,
    fsbo_only: bool = False,
) -> Dict:
    """
    Execute the RAG pipeline for property search.
    
    Args:
        query: User's natural language query
        price_max: Maximum price filter
        price_min: Minimum price filter
        bedrooms: Number of bedrooms filter
        location: Location/city filter
        fsbo_only: Only return FSBO properties
        
    Returns:
        Dictionary with 'answer' and 'context' (retrieved properties)
    """
    
    # Step 1: Initialize embeddings with dimension reduction
    embeddings = ReducedDimensionEmbeddings(model=EMBEDDING_MODEL)
    
    # Step 2: Connect to Pinecone vector store
    docsearch = PineconeVectorStore.from_existing_index(
        index_name=INDEX_NAME,
        embedding=embeddings
    )
    
    # Step 3: Build metadata filter
    filter_dict = {}
    
    if price_max:
        filter_dict["price"] = {"$lte": price_max}
    
    if price_min:
        if "price" in filter_dict:
            filter_dict["price"]["$gte"] = price_min
        else:
            filter_dict["price"] = {"$gte": price_min}
    
    if bedrooms:
        filter_dict["bedrooms"] = bedrooms
    
    if location:
        filter_dict["location"] = location
    
    if fsbo_only:
        filter_dict["is_fsbo"] = True
    
    # Step 4: Initialize LLM
    chat = ChatOpenAI(
        model=LLM_MODEL,
        temperature=0.3,  # Fairly deterministic for factual property info
        verbose=True
    )
    
    # Step 5: Get custom prompt
    retrieval_qa_prompt = get_property_search_prompt()
    
    # Step 6: Create the "stuff documents" chain
    # This takes retrieved docs and stuffs them into the prompt
    stuff_documents_chain = create_stuff_documents_chain(
        llm=chat,
        prompt=retrieval_qa_prompt
    )
    
    # Step 7: Create retrieval chain
    # This orchestrates: retrieval → augmentation → generation
    qa = create_retrieval_chain(
        retriever=docsearch.as_retriever(
            search_kwargs={
                "k": 8,  # Return top 8 most relevant properties
                "filter": filter_dict if filter_dict else None
            }
        ),
        combine_docs_chain=stuff_documents_chain
    )
    
    # Step 8: Execute the chain
    result = qa.invoke({"input": query})
    
    return result


def format_property_result(result: Dict) -> str:
    """
    Format the RAG result for display.
    """
    output = result["answer"] + "\n\n"
    output += "="*60 + "\n"
    output += "PROPERTY SOURCES:\n"
    output += "="*60 + "\n\n"
    
    for i, doc in enumerate(result["context"], 1):
        metadata = doc.metadata
        output += f"{i}. {metadata.get('source', 'Unknown')} - £{metadata.get('price', 0):,}\n"
        output += f"   📍 {metadata.get('location', 'Unknown')}\n"
        output += f"   🛏️  {metadata.get('bedrooms', 0)} bed, {metadata.get('bathrooms', 0)} bath\n"
        output += f"   🏠 {metadata.get('property_type', 'Unknown').title()}\n"
        
        if metadata.get('is_fsbo'):
            output += f"   ✅ FSBO (For Sale By Owner)\n"
        
        output += f"   🔗 {metadata.get('url', '')}\n\n"
    
    return output


# Test runner
if __name__ == "__main__":
    print("🏠 UK FSBO Property Search - RAG Test\n")
    
    # Test 1: Basic query
    print("TEST 1: Basic Property Search")
    print("-" * 60)
    query = "Show me 3-bedroom houses under £300,000 in Manchester"
    
    result = run_llm(
        query=query,
        bedrooms=3,
        price_max=300000,
        location="Manchester",
        fsbo_only=True
    )
    
    print(format_property_result(result))
    
    # Test 2: FSBO-specific query
    print("\nTEST 2: FSBO Search")
    print("-" * 60)
    query2 = "Find properties for sale by owner with no agent fees"
    
    result2 = run_llm(query=query2, fsbo_only=True)
    
    print(format_property_result(result2))
