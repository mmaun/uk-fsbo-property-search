# 🏠 UK FSBO Property Search System

An intelligent property search system that helps users find **For Sale By Owner (FSBO)** properties across the UK using RAG (Retrieval-Augmented Generation) technology.

## 🎯 Overview

This system transforms the documentation-helper project into a comprehensive UK property aggregator that:

- **Scrapes** 11 major UK property websites using Tavily AI
- **Detects** FSBO (For Sale By Owner) properties automatically
- **Indexes** properties in Pinecone vector database
- **Provides** intelligent search using GPT-4 and RAG
- **Displays** results in a beautiful Streamlit interface

## 🚀 Key Features

- ✅ **FSBO Detection**: Automatically identifies properties sold by owners
- ✅ **Smart Search**: Natural language queries with AI-powered responses
- ✅ **Advanced Filtering**: Price, location, bedrooms, FSBO status
- ✅ **Source Citations**: Direct links to original listings
- ✅ **Real-time Data**: Live property information from multiple sources
- ✅ **Beautiful UI**: Modern, responsive Streamlit interface

## 🏗️ Architecture

```
UK FSBO Property Search
├── ingestion/
│   └── ingest.py          # Tavily scraping + Pinecone indexing
├── backend/
│   └── core.py            # RAG implementation
├── frontend/
│   └── app.py             # Streamlit UI
├── requirements.txt       # Dependencies
├── env.example           # Environment variables template
└── README.md             # This file
```

## 🛠️ Technology Stack

- **Tavily**: Web scraping and content extraction
- **Pinecone**: Vector database for similarity search
- **OpenAI**: GPT-4 for responses + text-embedding-3-small for embeddings
- **LangChain**: RAG orchestration and chain management
- **Streamlit**: User interface
- **Python**: Backend implementation

## 📋 Prerequisites

1. **Python 3.11+**
2. **API Keys**:
   - OpenAI API key
   - Tavily API key
   - Pinecone API key

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd market-research-fsbo
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp env.example .env
```

Edit `.env` with your API keys:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Tavily Configuration
TAVILY_API_KEY=your_tavily_api_key_here

# Pinecone Configuration
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=your_pinecone_environment_here

# Index Configuration
INDEX_NAME=uk-fsbo-properties
```

### 4. Run Property Ingestion

```bash
python ingestion/ingest.py
```

This will:
- Scrape all 11 UK property websites
- Extract property details (price, beds, location, etc.)
- Detect FSBO properties
- Index everything in Pinecone

### 5. Start the Application

```bash
streamlit run frontend/app.py
```

## 🔍 Usage

### Basic Search

1. Open the Streamlit app
2. Set your filters (price, bedrooms, location, FSBO)
3. Enter a natural language query:
   - *"3-bedroom house in Manchester under £300k"*
   - *"FSBO properties in London"*
   - *"2-bed flat under £200k"*

4. Click "Search Properties"
5. Review AI recommendations and click through to original listings

### Advanced Features

- **FSBO Filter**: Toggle to show only owner-sold properties
- **Price Range**: Set minimum and maximum prices
- **Location**: Filter by city or area
- **Bedrooms**: Specify number of bedrooms
- **Source Citations**: See which website each property comes from

## 📊 Data Sources

The system scrapes these 11 UK property websites:

1. **Gumtree** - Popular classified ads
2. **TheHouseShop** - Direct sales platform
3. **OpenRent** - Rental and sales
4. **PropertyHeads** - FSBO specialist
5. **OnTheMarket** - Major property portal
6. **PropertyMutual** - Direct sales
7. **PropertyAdvertiser** - Private sales
8. **Houser** - Modern property platform
9. **NetHousePrices** - Property data
10. **Home.co.uk** - Property listings
11. **Facebook Marketplace** - Social selling

## 🤖 How RAG Works

### 1. Retrieval
- User query is converted to embeddings
- Similar properties are retrieved from Pinecone
- Metadata filters are applied (price, location, FSBO)

### 2. Augmentation
- Retrieved properties are combined with the user query
- Custom prompt template provides context to the LLM

### 3. Generation
- GPT-4 generates intelligent responses
- Results include property recommendations and source citations

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for GPT-4 and embeddings | Yes |
| `TAVILY_API_KEY` | Tavily API key for web scraping | Yes |
| `PINECONE_API_KEY` | Pinecone API key for vector database | Yes |
| `PINECONE_ENVIRONMENT` | Pinecone environment/region | Yes |
| `INDEX_NAME` | Pinecone index name (default: uk-fsbo-properties) | No |

### Customization

- **Property Sources**: Edit `PROPERTY_SOURCES` in `ingestion/ingest.py`
- **FSBO Keywords**: Modify `FSBO_KEYWORDS` for better detection
- **Search Filters**: Adjust filter logic in `backend/core.py`
- **UI Styling**: Customize CSS in `frontend/app.py`

## 🧪 Testing

### Test RAG Backend

```bash
python backend/core.py
```

### Test Ingestion

```bash
python ingestion/ingest.py
```

### Test Frontend

```bash
streamlit run frontend/app.py
```

## 📈 Performance

- **Scraping**: ~50-100 properties per source (adjustable)
- **Indexing**: ~1000 properties total
- **Search**: Sub-second response times
- **Accuracy**: High FSBO detection rate

## 🚨 Important Notes

- **Rate Limits**: Respect API rate limits for Tavily and OpenAI
- **Data Freshness**: Re-run ingestion periodically for fresh data
- **Verification**: Always verify property details on original websites
- **Scams**: Be cautious of potential property scams

## 🔒 Security

- API keys are stored in `.env` (never commit to git)
- No sensitive user data is stored
- All scraping respects website terms of service

## 🐛 Troubleshooting

### Common Issues

1. **API Key Errors**: Check your `.env` file
2. **Pinecone Connection**: Verify your environment and API key
3. **Scraping Failures**: Some websites may block automated requests
4. **Empty Results**: Try broader search terms or adjust filters

### Debug Mode

Enable verbose logging:

```python
# In backend/core.py
chat = ChatOpenAI(verbose=True, temperature=0.3)
```

## 📝 License

This project is based on the documentation-helper repository and adapted for UK property search.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the logs for error messages
3. Verify your API keys and configuration
4. Open an issue with detailed information

## 🎉 Success Metrics

After successful setup, you should see:
- ✅ Properties scraped from multiple sources
- ✅ FSBO properties detected and flagged
- ✅ Fast, intelligent search responses
- ✅ Beautiful property cards with source links
- ✅ Working filters and natural language queries

---

**Built with ❤️ for UK property buyers looking for FSBO deals!**