"""
UK FSBO Property Search - Streamlit Frontend
Beautiful and modern UI for property search with filters
"""

import streamlit as st
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.core import run_llm, format_property_result

# Page config
st.set_page_config(
    page_title="UK FSBO Property Search",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f4e79 0%, #2e7d32 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .property-card {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        background: #fafafa;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .fsbo-badge {
        background: #4caf50;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    
    .price-highlight {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2e7d32;
    }
    
    .source-badge {
        background: #2196f3;
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 15px;
        font-size: 0.7rem;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #1f4e79 0%, #2e7d32 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: bold;
    }
    
    .stButton > button:hover {
        background: linear-gradient(90deg, #2e7d32 0%, #1f4e79 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🏠 UK FSBO Property Search</h1>
    <p style="font-size: 1.2rem; margin: 0;">Find properties <strong>For Sale By Owner</strong> - No agent fees!</p>
</div>
""", unsafe_allow_html=True)

# Sidebar filters
with st.sidebar:
    st.header("🔍 Search Filters")
    
    # Price range
    st.subheader("💰 Price Range")
    price_min = st.number_input(
        "Min Price (£)",
        min_value=0,
        max_value=5000000,
        value=0,
        step=10000,
        help="Minimum price in British pounds"
    )
    price_max = st.number_input(
        "Max Price (£)",
        min_value=0,
        max_value=5000000,
        value=500000,
        step=10000,
        help="Maximum price in British pounds"
    )
    
    # Bedrooms
    st.subheader("🛏️ Property Details")
    bedrooms = st.selectbox(
        "Bedrooms",
        options=[None, 1, 2, 3, 4, 5, 6],
        format_func=lambda x: "Any" if x is None else f"{x} bedroom{'s' if x > 1 else ''}",
        help="Number of bedrooms"
    )
    
    # Location
    st.subheader("📍 Location")
    location = st.text_input(
        "City/Area",
        placeholder="e.g., Manchester, London, Birmingham",
        help="Enter city or area name"
    )
    
    # FSBO filter
    st.subheader("🏠 Property Type")
    fsbo_only = st.checkbox(
        "FSBO Only", 
        value=True,
        help="Show only For Sale By Owner properties"
    )
    
    # Info
    st.markdown("---")
    st.info("💡 **Tip**: Leave filters empty to search all properties")
    
    # Quick stats (placeholder)
    st.markdown("---")
    st.markdown("### 📊 Quick Stats")
    st.metric("Total Properties", "Loading...")
    st.metric("FSBO Properties", "Loading...")
    st.metric("Avg Price", "Loading...")

# Main content area
tab1, tab2, tab3 = st.tabs(["🔎 Search", "📋 Recent Searches", "ℹ️ About"])

with tab1:
    # Search input
    st.markdown("### 🎯 What property are you looking for?")
    query = st.text_input(
        "",
        placeholder="e.g., 3-bedroom house in Manchester under £300k",
        label_visibility="collapsed"
    )
    
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        search_button = st.button("🔍 Search Properties", type="primary", use_container_width=True)
    with col2:
        clear_button = st.button("🗑️ Clear", use_container_width=True)
    
    if clear_button:
        st.rerun()
    
    if search_button and query:
        with st.spinner("🔍 Searching properties... This may take a moment."):
            try:
                # Run RAG query
                result = run_llm(
                    query=query,
                    price_max=price_max if price_max > 0 else None,
                    price_min=price_min if price_min > 0 else None,
                    bedrooms=bedrooms,
                    location=location if location else None,
                    fsbo_only=fsbo_only
                )
                
                # Display answer
                st.markdown("### 💬 AI Assistant Response")
                st.markdown(result["answer"])
                
                # Display properties
                st.markdown("---")
                st.markdown("### 🏘️ Retrieved Properties")
                
                if result["context"]:
                    for i, doc in enumerate(result["context"], 1):
                        metadata = doc.metadata
                        
                        # Create property card
                        with st.container():
                            col1, col2 = st.columns([1, 3])
                            
                            with col1:
                                # Price display
                                st.markdown(f'<div class="price-highlight">£{metadata.get("price", 0):,}</div>', 
                                          unsafe_allow_html=True)
                                
                                # FSBO badge
                                if metadata.get('is_fsbo'):
                                    st.markdown('<span class="fsbo-badge">✅ FSBO</span>', 
                                              unsafe_allow_html=True)
                                else:
                                    st.markdown('<span style="background: #ff9800; color: white; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.8rem;">ℹ️ Standard</span>', 
                                              unsafe_allow_html=True)
                                
                                # Source badge
                                st.markdown(f'<span class="source-badge">{metadata.get("source", "Unknown")}</span>', 
                                          unsafe_allow_html=True)
                            
                            with col2:
                                # Property details
                                st.markdown(f"**{i}. {metadata.get('title', 'Property Listing')}**")
                                
                                # Location and details
                                details = f"📍 **{metadata.get('location', 'Unknown')}**"
                                if metadata.get('postcode'):
                                    details += f" ({metadata.get('postcode')})"
                                
                                details += f" | 🛏️ **{metadata.get('bedrooms', 0)} bed**"
                                if metadata.get('bathrooms', 0) > 0:
                                    details += f" | 🚿 **{metadata.get('bathrooms', 0)} bath**"
                                details += f" | 🏠 **{metadata.get('property_type', 'Unknown').title()}**"
                                
                                st.markdown(details)
                                
                                # FSBO indicators
                                if metadata.get('fsbo_indicators'):
                                    indicators = metadata['fsbo_indicators'].split(',')
                                    if indicators and indicators[0]:
                                        st.markdown(f"**FSBO Indicators**: {', '.join(indicators[:3])}")
                                
                                # View listing button
                                if metadata.get('url'):
                                    st.link_button(
                                        "🔗 View Full Listing",
                                        metadata['url'],
                                        type="secondary"
                                    )
                            
                            st.markdown("---")
                else:
                    st.warning("No properties found matching your criteria. Try adjusting your filters or search terms.")
                    
            except Exception as e:
                st.error(f"Error searching properties: {str(e)}")
                st.info("Please check your API keys and try again.")
    
    elif search_button:
        st.warning("Please enter a search query.")

with tab2:
    st.markdown("### 📋 Recent Searches")
    st.info("Recent search history will appear here once you start searching.")
    
    # Placeholder for search history
    if 'search_history' not in st.session_state:
        st.session_state.search_history = []
    
    if st.session_state.search_history:
        for i, search in enumerate(st.session_state.search_history[-5:]):
            with st.expander(f"Search {i+1}: {search['query'][:50]}..."):
                st.write(f"**Query**: {search['query']}")
                st.write(f"**Filters**: {search['filters']}")
                st.write(f"**Results**: {search['result_count']} properties found")
    else:
        st.markdown("No searches yet. Start searching to see your history here!")

with tab3:
    st.markdown("""
    ## About UK FSBO Property Search
    
    This intelligent property search system helps you find **For Sale By Owner (FSBO)** properties across the UK.
    
    ### 🎯 What is FSBO?
    FSBO properties are sold directly by the owner without an estate agent, which means:
    - ✅ **No agent commission** (save thousands!)
    - ✅ **Direct negotiation** with owner
    - ✅ **Potentially better deals**
    - ✅ **More flexible terms**
    
    ### 🌐 Data Sources
    We search across 11 major UK property websites:
    - **Gumtree** - Popular classified ads
    - **TheHouseShop** - Direct sales platform
    - **OpenRent** - Rental and sales
    - **PropertyHeads** - FSBO specialist
    - **OnTheMarket** - Major property portal
    - **PropertyMutual** - Direct sales
    - **PropertyAdvertiser** - Private sales
    - **Houser** - Modern property platform
    - **NetHousePrices** - Property data
    - **Home.co.uk** - Property listings
    - **Facebook Marketplace** - Social selling
    
    ### 🤖 How It Works
    1. **Scraping**: We use Tavily AI to scrape property listings
    2. **Indexing**: Properties are stored in Pinecone vector database
    3. **Smart Search**: AI-powered semantic search finds the best matches
    4. **RAG**: Retrieval-Augmented Generation provides intelligent answers
    
    ### 💡 Search Tips
    - Use natural language: *"3-bed house in Manchester under £300k"*
    - Enable FSBO filter to see only owner-sold properties
    - Adjust price and bedroom filters for better results
    - Check multiple properties to compare
    - Look for FSBO indicators like "no agent fees" or "private sale"
    
    ### 🔧 Technology Stack
    - **Tavily**: Web scraping and content extraction
    - **Pinecone**: Vector database for similarity search
    - **OpenAI**: GPT-4 for intelligent responses + embeddings
    - **LangChain**: RAG orchestration and chain management
    - **Streamlit**: Beautiful user interface
    
    ### 📊 Features
    - **Smart Filtering**: Price, location, bedrooms, FSBO status
    - **AI-Powered Search**: Natural language queries
    - **Source Citations**: Direct links to original listings
    - **FSBO Detection**: Automatic identification of owner sales
    - **Real-time Results**: Live property data
    
    ### 🚀 Getting Started
    1. Set your price range and filters
    2. Enter a natural language search query
    3. Click "Search Properties"
    4. Review AI recommendations
    5. Click through to original listings
    
    ### ⚠️ Important Notes
    - Always verify property details on the original website
    - Contact sellers directly through the original platform
    - Be cautious of potential scams (never send money upfront)
    - Consider getting a property survey before purchasing
    
    ### 📞 Support
    If you encounter any issues or have suggestions, please check the system logs or contact support.
    """)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #666; padding: 1rem;">
        🏠 <strong>UK FSBO Property Search</strong> | 
        Powered by Tavily, Pinecone, OpenAI & LangChain | 
        Built with ❤️ for UK property buyers
    </div>
    """, 
    unsafe_allow_html=True
)
