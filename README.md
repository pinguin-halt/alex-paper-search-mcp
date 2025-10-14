# OpenAlex Paper Search MCP Server

A Model Context Protocol (MCP) server that provides comprehensive access to the [OpenAlex](https://openalex.org/) academic database. Search and retrieve academic papers, authors, institutions, and more with advanced filtering capabilities.

## Features

- 🔍 **Comprehensive Search**: Search across hundreds of millions of academic works
- 🎯 **Advanced Filtering**: Filter by date, open access status, citations, country, language, and more
- 📊 **Rich Metadata**: Get detailed information including abstracts, citations, topics, and full bibliographic data
- 🚀 **High Performance**: Optimized for fast responses with proper API configuration
- 🐳 **Docker Ready**: Easy deployment with Docker and Docker Compose
- 🔧 **MCP Compatible**: Works with any MCP-compatible client

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/LeoGitGuy/alex-paper-search-mcp.git
cd openalex-mcp-server

# Install dependencies
pip install -e .

# Set your email for better API performance (optional but recommended)
export OPENALEX_EMAIL="your.email@example.com"

# Run the server
python -m openalex_mcp.server
```

### Docker Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env to set your email
echo "OPENALEX_EMAIL=your.email@example.com" > .env

# Run with Docker Compose
docker-compose up -d
```

### Claude Desktop Integration

To use this MCP server with Claude Desktop, add this configuration to your Claude Desktop config file:

**Mac**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "openalex_paper_search": {
      "command": "python",
      "args": [
        "-m",
        "openalex_mcp.server"
      ],
      "cwd": "/path/to/your/openalex-mcp-server",
      "env": {
        "OPENALEX_EMAIL": "your.email@example.com"
      }
    }
  }
}
```

Make sure to:
1. Replace `/path/to/your/openalex-mcp-server` with the actual path to your cloned repository
2. Replace `your.email@example.com` with your actual email address for better API performance
3. Restart Claude Desktop after updating the configuration

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENALEX_EMAIL` | Recommended | Your email for OpenAlex polite pool access (faster response times) |
| `OPENALEX_API_KEY` | Optional | API key for authenticated requests (experimental feature) |

### Why Set an Email?

Setting `OPENALEX_EMAIL` gives you access to OpenAlex's "polite pool", which includes faster response times and higher rate limits

## Available Tools

### Core Search Functions

#### `search_openalex`
Main search function with full filtering capabilities:

```python
# Basic search
search_openalex("machine learning", max_results=20)

# Advanced filtering
search_openalex(
    "neural networks", 
    max_results=15,
    from_publication_date="2020-01-01",
    is_oa=True,
    cited_by_count=">100",
    institution_country="us"
)
```

#### `get_paper_by_id` / `get_paper_by_doi`
Retrieve specific papers:

```python
get_paper_by_id("W2741809807")
get_paper_by_doi("10.7717/peerj.4375")
```

### Convenience Functions

#### `search_open_access_papers`
Find freely available research:

```python
search_open_access_papers(
    "artificial intelligence",
    max_results=15,
    from_publication_date="2020-01-01"
)
```

#### `search_recent_papers`
Get the latest research:

```python
search_recent_papers(
    "quantum computing",
    max_results=20,
    years_back=3,
    min_citations=10
)
```

#### `search_by_institution`
Find research from specific countries:

```python
search_by_institution(
    "renewable energy",
    institution_country="de",  # Germany
    max_results=15
)
```

## Filtering Options

### Date Filters
- `from_publication_date`: "YYYY-MM-DD" (published on or after)
- `to_publication_date`: "YYYY-MM-DD" (published on or before)  
- `publication_year`: Integer (exact year)

### Content Filters
- `is_oa`: Boolean (open access only)
- `has_doi`: Boolean (papers with DOI)
- `has_fulltext`: Boolean (fulltext available)
- `has_abstract`: Boolean (abstract available)
- `type`: String ('article', 'book', 'dataset', etc.)

### Quality Filters
- `cited_by_count`: String (">50", "10-100", ">=5")
- `authors_count`: String (">1", "1-5") 
- `language`: String ('en', 'zh', 'es', etc.)

### Institution & Geographic Filters
- `institution_country`: String ('us', 'gb', 'cn', 'de', etc.)
- `funder`: String (funder name or ID)
- `journal`: String (OpenAlex journal ID)

### Text Search Filters
- `abstract_search`: Search within abstracts
- `title_search`: Search within titles
- `fulltext_search`: Search within fulltext (where available)

### Sorting Options
- `sort`: 'cited_by_count', 'publication_date', 'relevance_score'
- `order`: 'desc', 'asc'

## Usage Examples

### Find Highly Cited Recent Papers
```python
search_openalex(
    "deep learning",
    max_results=10,
    from_publication_date="2023-01-01",
    cited_by_count=">100",
    sort="cited_by_count",
    order="desc"
)
```

### Search Open Access Climate Research
```python
search_open_access_papers(
    "climate change adaptation",
    max_results=20,
    from_publication_date="2020-01-01",
    type="article"
)
```

### Find Papers by Abstract Content
```python
search_openalex(
    "",  # Empty main query
    max_results=15,
    abstract_search="machine learning ethics",
    is_oa=True
)
```

### Get Recent COVID Research from Multiple Countries
```python
# US research
us_papers = search_by_institution("COVID-19", "us", 10, from_publication_date="2023-01-01")

# British research  
gb_papers = search_by_institution("COVID-19", "gb", 10, from_publication_date="2023-01-01")
```

## Troubleshooting

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python -m openalex_mcp.server
```

### Check Configuration

```python
# Test your email configuration
from openalex_mcp.searcher import OpenAlexSearcher
searcher = OpenAlexSearcher(email="your.email@example.com")
papers = searcher.search("test", 1)
print(f"Found {len(papers)} papers")
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- [OpenAlex](https://openalex.org/) for providing free access to academic data
- [PyAlex](https://github.com/J535D165/pyalex) for the excellent Python library
