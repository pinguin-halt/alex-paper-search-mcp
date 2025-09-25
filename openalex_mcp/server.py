#!/usr/bin/env python3
"""
OpenAlex MCP Server

A Model Context Protocol (MCP) server that provides comprehensive access to the 
OpenAlex academic database with advanced filtering and search capabilities.

OpenAlex is a comprehensive index of scholarly papers, authors, institutions,
and more, providing access to hundreds of millions of interconnected academic works.
"""

import os
import logging
from typing import List, Dict, Optional
from mcp.server.fastmcp import FastMCP
from .searcher import OpenAlexSearcher

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP("openalex_mcp_server")

# Initialize OpenAlex searcher with email from environment variable
openalex_email = os.getenv('OPENALEX_EMAIL')
openalex_api_key = os.getenv('OPENALEX_API_KEY')

if not openalex_email:
    logger.warning(
        "OPENALEX_EMAIL not set. Consider setting it for better API performance. "
        "Set with: export OPENALEX_EMAIL=your.email@example.com"
    )

searcher = OpenAlexSearcher(email=openalex_email, api_key=openalex_api_key)


@mcp.tool()
async def search_openalex(
    query: str, 
    max_results: int = 10, 
    from_publication_date: Optional[str] = None,
    to_publication_date: Optional[str] = None,
    publication_year: Optional[int] = None,
    is_oa: Optional[bool] = None,
    has_doi: Optional[bool] = None,
    has_fulltext: Optional[bool] = None,
    has_abstract: Optional[bool] = None,
    type: Optional[str] = None,
    cited_by_count: Optional[str] = None,
    authors_count: Optional[str] = None,
    institution_country: Optional[str] = None,
    language: Optional[str] = None,
    journal: Optional[str] = None,
    repository: Optional[str] = None,
    funder: Optional[str] = None,
    abstract_search: Optional[str] = None,
    title_search: Optional[str] = None,
    fulltext_search: Optional[str] = None,
    sort: Optional[str] = None,
    order: Optional[str] = None
) -> List[Dict]:
    """Search academic papers from OpenAlex with advanced filtering.
    
    OpenAlex is a comprehensive index of scholarly papers, authors, institutions,
    and more, providing access to hundreds of millions of interconnected academic works.

    Args:
        query: Search query string (e.g., 'machine learning', 'climate change').
        max_results: Maximum number of papers to return (default: 10).
        from_publication_date: Published on or after this date (format: "YYYY-MM-DD").
        to_publication_date: Published on or before this date (format: "YYYY-MM-DD").
        publication_year: Published in this exact year (integer).
        is_oa: Filter for open access papers (true/false).
        has_doi: Filter for papers with DOI (true/false).
        has_fulltext: Filter for papers with fulltext available (true/false).
        has_abstract: Filter for papers with abstracts available (true/false).
        type: Work type filter ('article', 'book', 'dataset', 'dissertation', etc.).
        cited_by_count: Citation count filter:
            - Exact: "100"
            - Range: "10-100"  
            - Comparison: ">50", ">=10", "<1000"
        authors_count: Number of authors filter (e.g., ">1", "1-5", "1").
        institution_country: Filter by institution country code ('us', 'gb', 'cn', etc.).
        language: Filter by language code ('en', 'zh', 'es', 'fr', etc.).
        journal: Filter by journal OpenAlex ID (e.g., "S137773608").
        repository: Filter by repository OpenAlex ID (e.g., "S4306400393").
        funder: Filter by funder name or ID.
        abstract_search: Text search within abstracts.
        title_search: Text search within titles.
        fulltext_search: Text search within fulltext (where available).
        sort: Sort field ('cited_by_count', 'publication_date', 'relevance_score').
        order: Sort order ('desc', 'asc').
        
    Returns:
        List of paper metadata in dictionary format.
        
    Examples:
        # Basic search
        search_openalex("deep learning", 20)
        
        # Papers published after 2020
        search_openalex("neural networks", 15, from_publication_date="2020-01-01", is_oa=true)
        
        # Highly cited articles in 2023
        search_openalex("climate change", 10, publication_year=2023, cited_by_count=">100")
        
        # Search abstracts for specific terms
        search_openalex("", 10, abstract_search="machine learning ethics")
    """
    # Build kwargs for filtering
    kwargs = {}
    if from_publication_date is not None:
        kwargs['from_publication_date'] = from_publication_date
    if to_publication_date is not None:
        kwargs['to_publication_date'] = to_publication_date
    if publication_year is not None:
        kwargs['publication_year'] = publication_year
    if is_oa is not None:
        kwargs['is_oa'] = is_oa
    if has_doi is not None:
        kwargs['has_doi'] = has_doi
    if has_fulltext is not None:
        kwargs['has_fulltext'] = has_fulltext
    if has_abstract is not None:
        kwargs['has_abstract'] = has_abstract
    if type is not None:
        kwargs['type'] = type
    if cited_by_count is not None:
        kwargs['cited_by_count'] = cited_by_count
    if authors_count is not None:
        kwargs['authors_count'] = authors_count
    if institution_country is not None:
        kwargs['institution_country'] = institution_country
    if language is not None:
        kwargs['language'] = language
    if journal is not None:
        kwargs['journal'] = journal
    if repository is not None:
        kwargs['repository'] = repository
    if funder is not None:
        kwargs['funder'] = funder
    if abstract_search is not None:
        kwargs['abstract_search'] = abstract_search
    if title_search is not None:
        kwargs['title_search'] = title_search
    if fulltext_search is not None:
        kwargs['fulltext_search'] = fulltext_search
    if sort is not None:
        kwargs['sort'] = sort
    if order is not None:
        kwargs['order'] = order
    
    papers = searcher.search(query, max_results, **kwargs)
    return [paper.to_dict() for paper in papers] if papers else []


@mcp.tool()
async def get_paper_by_id(openalex_id: str) -> Dict:
    """Get a specific paper from OpenAlex by its ID.

    Args:
        openalex_id: OpenAlex work ID (e.g., 'W2741809807' or 'https://openalex.org/W2741809807').
        
    Returns:
        Paper metadata in dictionary format, or empty dict if not found.
        
    Example:
        get_paper_by_id("W2741809807")
    """
    paper = searcher.get_paper_by_id(openalex_id)
    return paper.to_dict() if paper else {}


@mcp.tool()
async def get_paper_by_doi(doi: str) -> Dict:
    """Get a specific paper from OpenAlex by its DOI.

    Args:
        doi: Digital Object Identifier (e.g., '10.7717/peerj.4375').
        
    Returns:
        Paper metadata in dictionary format, or empty dict if not found.
        
    Example:
        get_paper_by_doi("10.7717/peerj.4375")
    """
    paper = searcher.get_paper_by_doi(doi)
    return paper.to_dict() if paper else {}


@mcp.tool()
async def read_paper_content(paper_id: str) -> str:
    """Read and extract metadata content from an OpenAlex paper.

    Args:
        paper_id: OpenAlex work ID (e.g., 'W2741809807').
        
    Returns:
        The extracted paper metadata and abstract content.
        
    Example:
        read_paper_content("W2741809807")
    """
    return searcher.read_paper(paper_id)


@mcp.tool()
async def get_pdf_info(paper_id: str) -> str:
    """Get information about PDF download options for an OpenAlex paper.

    Args:
        paper_id: OpenAlex work ID (e.g., 'W2741809807').
        
    Returns:
        Information about how to access the paper's PDF.
        
    Note:
        OpenAlex doesn't provide direct PDF downloads. This tool provides 
        information about where to find the PDF through publishers or repositories.
    """
    return searcher.get_pdf_info(paper_id)


@mcp.tool()
async def search_open_access_papers(
    query: str, 
    max_results: int = 10,
    from_publication_date: Optional[str] = None,
    to_publication_date: Optional[str] = None,
    publication_year: Optional[int] = None,
    type: Optional[str] = "article",
    sort: Optional[str] = "cited_by_count",
    order: Optional[str] = "desc"
) -> List[Dict]:
    """Search for open access papers only with common filtering options.
    
    This is a convenience function that automatically filters for open access papers
    and commonly used parameters for finding high-quality, accessible research.

    Args:
        query: Search query string (e.g., 'machine learning', 'climate change').
        max_results: Maximum number of papers to return (default: 10).
        from_publication_date: Published on or after this date (format: "YYYY-MM-DD").
        to_publication_date: Published on or before this date (format: "YYYY-MM-DD").
        publication_year: Published in this exact year (integer).
        type: Work type filter (default: 'article').
        sort: Sort field (default: 'cited_by_count').
        order: Sort order (default: 'desc').
        
    Returns:
        List of open access paper metadata in dictionary format.
        
    Example:
        search_open_access_papers("artificial intelligence", 15, from_publication_date="2020-01-01")
    """
    kwargs = {
        'is_oa': True,
        'has_doi': True,
        'has_fulltext': True,
        'sort': sort,
        'order': order
    }
    
    if from_publication_date is not None:
        kwargs['from_publication_date'] = from_publication_date
    if to_publication_date is not None:
        kwargs['to_publication_date'] = to_publication_date
    if publication_year is not None:
        kwargs['publication_year'] = publication_year
    if type is not None:
        kwargs['type'] = type
    
    papers = searcher.search(query, max_results, **kwargs)
    return [paper.to_dict() for paper in papers] if papers else []


@mcp.tool()
async def search_recent_papers(
    query: str,
    max_results: int = 10,
    years_back: int = 2,
    min_citations: int = 0
) -> List[Dict]:
    """Search for recent papers with optional minimum citation filtering.
    
    This convenience function searches for papers published in recent years,
    useful for finding the latest research in a field.

    Args:
        query: Search query string.
        max_results: Maximum number of papers to return (default: 10).
        years_back: How many years back to search from current year (default: 2).
        min_citations: Minimum number of citations (default: 0).
        
    Returns:
        List of recent paper metadata in dictionary format.
        
    Example:
        search_recent_papers("quantum computing", 20, years_back=3, min_citations=10)
    """
    from datetime import datetime
    current_year = datetime.now().year
    start_year = current_year - years_back
    
    kwargs = {
        'from_publication_date': f"{start_year}-01-01",
        'sort': 'publication_date',
        'order': 'desc'
    }
    
    if min_citations > 0:
        kwargs['cited_by_count'] = f">={min_citations}"
    
    papers = searcher.search(query, max_results, **kwargs)
    return [paper.to_dict() for paper in papers] if papers else []


@mcp.tool()
async def search_by_institution(
    query: str,
    institution_country: str,
    max_results: int = 10,
    from_publication_date: Optional[str] = None,
    to_publication_date: Optional[str] = None,
    publication_year: Optional[int] = None
) -> List[Dict]:
    """Search for papers by institution country with optional date filtering.
    
    This function helps find research output from specific countries or regions.

    Args:
        query: Search query string.
        institution_country: Country code (e.g., 'us', 'gb', 'cn', 'de', 'jp').
        max_results: Maximum number of papers to return (default: 10).
        from_publication_date: Published on or after this date (format: "YYYY-MM-DD").
        to_publication_date: Published on or before this date (format: "YYYY-MM-DD").
        publication_year: Published in this exact year (integer).
        
    Returns:
        List of paper metadata from specified institutions.
        
    Example:
        search_by_institution("renewable energy", "us", 15, from_publication_date="2020-01-01")
    """
    kwargs = {
        'institution_country': institution_country,
        'sort': 'cited_by_count',
        'order': 'desc'
    }
    
    if from_publication_date is not None:
        kwargs['from_publication_date'] = from_publication_date
    if to_publication_date is not None:
        kwargs['to_publication_date'] = to_publication_date
    if publication_year is not None:
        kwargs['publication_year'] = publication_year
    
    papers = searcher.search(query, max_results, **kwargs)
    return [paper.to_dict() for paper in papers] if papers else []


def main():
    """Main entry point for the server."""
    logger.info("Starting OpenAlex MCP Server...")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()