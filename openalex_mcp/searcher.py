# openalex_mcp/searcher.py
"""OpenAlex searcher implementation for MCP server."""
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
import pyalex
from pyalex import Works, config
from .paper import Paper

logger = logging.getLogger(__name__)

class OpenAlexSearcher:
    """OpenAlex academic paper search using PyAlex"""
    
    def __init__(self, email: Optional[str] = None, api_key: Optional[str] = None):
        """Initialize OpenAlex searcher
        
        Args:
            email: Email for polite pool access (faster response times)
            api_key: API key for authenticated requests (experimental)
        """
        # Configure pyalex
        config.max_retries = 3
        config.retry_backoff_factor = 0.1
        config.retry_http_codes = [429, 500, 503]
        
        if email:
            config.email = email
        if api_key:
            config.api_key = api_key
            
        logger.info("OpenAlex searcher initialized")

    def search(self, query: str, max_results: int = 10, **kwargs) -> List[Paper]:
        """Search papers using OpenAlex
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            **kwargs: Advanced filter options:
                - from_publication_date: Date filter "YYYY-MM-DD" (published on or after)
                - to_publication_date: Date filter "YYYY-MM-DD" (published on or before)
                - publication_year: Single year (int) for exact year matching
                - is_oa: Filter for open access papers (bool)
                - has_doi: Filter for papers with DOI (bool) 
                - has_fulltext: Filter for papers with fulltext (bool)
                - has_abstract: Filter for papers with abstracts (bool)
                - type: Work type (e.g., 'article', 'book', 'dataset')
                - cited_by_count: Citation count filter (e.g., ">10", "5-50")
                - authors_count: Number of authors filter (e.g., ">1", "1-5")
                - institution_country: Country code (e.g., 'us', 'gb')
                - language: Language code (e.g., 'en', 'zh')
                - journal: Journal OpenAlex ID
                - repository: Repository OpenAlex ID
                - funder: Funder name or ID
                - abstract_search: Text search in abstracts
                - title_search: Text search in titles
                - fulltext_search: Text search in fulltext
                - sort: Sort field ('cited_by_count', 'publication_date', 'relevance_score')
                - order: Sort order ('desc', 'asc')
                
        Returns:
            List of Paper objects
        """
        try:
            logger.info(f"Searching OpenAlex for: {query}")
            
            # Start with basic search query
            works_query = Works().search(query)
            
            # Apply filters using the proper PyAlex filter() method
            works_query = self._apply_convenience_filters(works_query, **kwargs)
            
            # Apply sorting
            sort_field = kwargs.get('sort', 'relevance_score')
            sort_order = kwargs.get('order', 'desc')
            if sort_field != 'relevance_score':  # relevance_score is default, no explicit sort needed
                # PyAlex sort method takes keyword arguments
                sort_kwargs = {sort_field: sort_order}
                works_query = works_query.sort(**sort_kwargs)
            
            # Get results
            results = works_query.get()[:max_results]
            
            papers = []
            for work in results:
                try:
                    paper = self._convert_to_paper(work)
                    if paper:
                        papers.append(paper)
                except Exception as e:
                    logger.warning(f"Failed to convert work to paper: {e}")
                    continue
                    
            logger.info(f"Found {len(papers)} papers from OpenAlex")
            return papers
            
        except Exception as e:
            logger.error(f"OpenAlex search failed: {e}")
            return []

    def _apply_convenience_filters(self, works_query, **kwargs):
        """Apply convenience filters using PyAlex's filter() method"""
        
        # Date filters using convenience filters
        if 'from_publication_date' in kwargs:
            works_query = works_query.filter(from_publication_date=kwargs['from_publication_date'])
        if 'to_publication_date' in kwargs:
            works_query = works_query.filter(to_publication_date=kwargs['to_publication_date'])
            
        # Single year filter (still using publication_year for exact matches)
        if 'publication_year' in kwargs:
            year_value = kwargs['publication_year']
            if isinstance(year_value, (int, str)):
                works_query = works_query.filter(publication_year=year_value)
        
        # Boolean filters
        if kwargs.get('is_oa') is not None:
            works_query = works_query.filter(is_oa=kwargs['is_oa'])
        if kwargs.get('has_doi') is not None:
            works_query = works_query.filter(has_doi=kwargs['has_doi'])
        if kwargs.get('has_fulltext') is not None:
            works_query = works_query.filter(has_fulltext=kwargs['has_fulltext'])
        if kwargs.get('has_abstract') is not None:
            works_query = works_query.filter(has_abstract=kwargs['has_abstract'])
            
        # Work type filter
        if 'type' in kwargs:
            works_query = works_query.filter(type=kwargs['type'])
            
        # Citation count filter
        if 'cited_by_count' in kwargs:
            works_query = works_query.filter(cited_by_count=kwargs['cited_by_count'])
            
        # Authors count filter
        if 'authors_count' in kwargs:
            works_query = works_query.filter(authors_count=kwargs['authors_count'])
            
        # Institution country filter using nested structure
        if 'institution_country' in kwargs:
            works_query = works_query.filter(
                institutions={"country_code": kwargs['institution_country']}
            )
            
        # Language filter
        if 'language' in kwargs:
            works_query = works_query.filter(language=kwargs['language'])
            
        # Journal filter (expects OpenAlex ID)
        if 'journal' in kwargs:
            works_query = works_query.filter(journal=kwargs['journal'])
            
        # Repository filter (expects OpenAlex ID)
        if 'repository' in kwargs:
            works_query = works_query.filter(repository=kwargs['repository'])
                
        # Funder filter
        if 'funder' in kwargs:
            works_query = works_query.filter(grants={"funder": kwargs['funder']})
            
        # Text search filters using convenience filters
        if 'abstract_search' in kwargs:
            works_query = works_query.filter(**{"abstract.search": kwargs['abstract_search']})
        if 'title_search' in kwargs:
            works_query = works_query.filter(**{"title.search": kwargs['title_search']})
        if 'fulltext_search' in kwargs:
            works_query = works_query.filter(**{"fulltext.search": kwargs['fulltext_search']})
            
        return works_query

    def _convert_to_paper(self, work: Dict[str, Any]) -> Optional[Paper]:
        """Convert OpenAlex work to Paper object"""
        try:
            # Extract basic information
            paper_id = work.get('id', '').replace('https://openalex.org/', '')
            title = work.get('title', '') or work.get('display_name', '')
            abstract = work['abstract']
            doi = work.get('doi', '').replace('https://doi.org/', '') if work.get('doi') else ''
            
            # Extract authors
            authors = []
            for authorship in work.get('authorships', []):
                author_name = authorship.get('author', {}).get('display_name')
                if author_name:
                    authors.append(author_name)
            
            # Extract dates
            published_date = None
            pub_date_str = work.get('publication_date')
            if pub_date_str:
                try:
                    published_date = datetime.fromisoformat(pub_date_str.replace('Z', '+00:00'))
                except:
                    # Try parsing just the date part
                    try:
                        published_date = datetime.strptime(pub_date_str[:10], '%Y-%m-%d')
                    except:
                        pass
            
            # Extract URLs
            pdf_url = ''
            url = work.get('id', '')  # OpenAlex ID as fallback URL
            
            # Try to get PDF URL from open access location
            best_oa_location = work.get('best_oa_location')
            if best_oa_location:
                pdf_url = best_oa_location.get('pdf_url', '') or best_oa_location.get('landing_page_url', '')
                url = best_oa_location.get('landing_page_url', url)
            
            # If no PDF from OA location, try primary location
            if not pdf_url:
                primary_location = work.get('primary_location')
                if primary_location:
                    pdf_url = primary_location.get('pdf_url', '') or primary_location.get('landing_page_url', '')
                    if not url or url == work.get('id', ''):
                        url = primary_location.get('landing_page_url', url)
            
            # Extract categories/topics
            categories = []
            topics = work.get('topics', [])
            for topic in topics[:3]:  # Limit to top 3 topics
                topic_name = topic.get('display_name')
                if topic_name:
                    categories.append(topic_name)
            
            # Extract keywords from concepts (deprecated but still might be present)
            keywords = []
            concepts = work.get('concepts', [])
            for concept in concepts[:5]:  # Limit to top 5 concepts
                concept_name = concept.get('display_name')
                if concept_name and concept.get('score', 0) > 0.3:  # Only high-confidence concepts
                    keywords.append(concept_name)
            
            # Extract additional metadata
            citations = work.get('cited_by_count', 0)
            
            # Build extra metadata
            extra = {
                'openalex_id': work.get('id', ''),
                'publication_year': work.get('publication_year'),
                'type': work.get('type'),
                'open_access': work.get('open_access', {}),
                'relevance_score': work.get('relevance_score'),
                'language': work.get('language'),
                'countries_distinct_count': work.get('countries_distinct_count'),
                'institutions_distinct_count': work.get('institutions_distinct_count'),
                'corresponding_author_ids': work.get('corresponding_author_ids', []),
                'primary_topic': work.get('primary_topic', {}),
                'sustainable_development_goals': work.get('sustainable_development_goals', []),
                'grants': work.get('grants', []),
            }
            
            # Handle updated date
            updated_date = None
            update_date_str = work.get('updated_date')
            if update_date_str:
                try:
                    updated_date = datetime.fromisoformat(update_date_str.replace('Z', '+00:00'))
                except:
                    pass
            
            return Paper(
                paper_id=paper_id,
                title=title,
                authors=authors,
                abstract=abstract,
                doi=doi,
                published_date=published_date,
                pdf_url=pdf_url,
                url=url,
                source='openalex',
                updated_date=updated_date,
                categories=categories,
                keywords=keywords,
                citations=citations,
                extra=extra
            )
            
        except Exception as e:
            logger.error(f"Failed to convert OpenAlex work: {e}")
            return None

    def get_paper_by_doi(self, doi: str) -> Optional[Paper]:
        """Get a specific paper by DOI
        
        Args:
            doi: Digital Object Identifier
            
        Returns:
            Paper object or None if not found
        """
        try:
            # Clean DOI
            if not doi.startswith('https://doi.org/'):
                doi = f"https://doi.org/{doi}"
            
            work = Works()[doi]
            return self._convert_to_paper(work)
            
        except Exception as e:
            logger.error(f"Failed to get paper by DOI {doi}: {e}")
            return None

    def get_paper_by_id(self, openalex_id: str) -> Optional[Paper]:
        """Get a specific paper by OpenAlex ID
        
        Args:
            openalex_id: OpenAlex work ID (with or without URL prefix)
            
        Returns:
            Paper object or None if not found
        """
        try:
            # Clean the ID
            if openalex_id.startswith('https://openalex.org/'):
                clean_id = openalex_id
            elif openalex_id.startswith('W'):
                clean_id = f"https://openalex.org/{openalex_id}"
            else:
                clean_id = f"https://openalex.org/W{openalex_id}"
            
            work = Works()[clean_id]
            return self._convert_to_paper(work)
            
        except Exception as e:
            logger.error(f"Failed to get paper by ID {openalex_id}: {e}")
            return None

    def read_paper(self, paper_id: str) -> str:
        """Read paper content from OpenAlex
        
        Args:
            paper_id: OpenAlex work ID
            
        Returns:
            Paper text content
        """
        try:
            # Clean the paper ID
            if paper_id.startswith('https://openalex.org/'):
                clean_id = paper_id
            elif paper_id.startswith('W'):
                clean_id = f"https://openalex.org/{paper_id}"
            else:
                clean_id = f"https://openalex.org/W{paper_id}"
            
            # Get the work
            work = Works()[clean_id]
            
            # Extract text content
            content_parts = []
            
            # Add title
            title = work.get('title') or work.get('display_name', '')
            if title:
                content_parts.append(f"Title: {title}\n")
            
            # Add authors
            authors = []
            for authorship in work.get('authorships', []):
                author_name = authorship.get('author', {}).get('display_name')
                if author_name:
                    authors.append(author_name)
            if authors:
                content_parts.append(f"Authors: {'; '.join(authors)}\n")
            
            # Add abstract
            abstract = work['abstract']
            if abstract:
                content_parts.append(f"Abstract: {abstract}\n")
            
            # Add publication info
            pub_year = work.get('publication_year')
            if pub_year:
                content_parts.append(f"Publication Year: {pub_year}\n")
            
            # Add topics
            topics = work.get('topics', [])
            if topics:
                topic_names = [topic.get('display_name') for topic in topics[:3] if topic.get('display_name')]
                if topic_names:
                    content_parts.append(f"Topics: {'; '.join(topic_names)}\n")
            
            return '\n'.join(content_parts) if content_parts else "No content available"
            
        except Exception as e:
            logger.error(f"Failed to read OpenAlex paper {paper_id}: {e}")
            return f"Error reading paper: {e}"

    def get_pdf_info(self, paper_id: str) -> str:
        """Get information about PDF download options for an OpenAlex paper
        
        Args:
            paper_id: OpenAlex work ID
            
        Returns:
            Information about how to access the paper's PDF
        """
        return (
            "OpenAlex doesn't provide direct PDF downloads. "
            "Use the PDF URL from search results to download from the publisher or repository. "
            "Look for 'pdf_url' in the paper metadata, or check open access locations."
        )