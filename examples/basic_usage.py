#!/usr/bin/env python3
"""
Example usage of OpenAlex MCP Server
This script demonstrates how to use the searcher directly without MCP.
"""

import asyncio
import os
from openalex_mcp.searcher import OpenAlexSearcher

async def main():
    """Demonstrate OpenAlex searcher functionality"""
    
    # Initialize searcher
    email = os.getenv('OPENALEX_EMAIL', 'example@example.com')
    searcher = OpenAlexSearcher(email=email)
    
    print("🔬 OpenAlex MCP Server Examples")
    print("=" * 50)
    
    # Example 1: Basic search
    print("\n1. Basic Search - Machine Learning Papers")
    papers = searcher.search("machine learning", max_results=5)
    
    for i, paper in enumerate(papers, 1):
        print(f"\n{i}. {paper.title}")
        print(f"   Authors: {', '.join(paper.authors[:3])}{'...' if len(paper.authors) > 3 else ''}")
        print(f"   Citations: {paper.citations}")
        print(f"   Year: {paper.extra.get('publication_year', 'N/A')}")
        print(f"   Open Access: {paper.extra.get('open_access', {}).get('is_oa', False)}")
        abstract = paper.abstract
        print(f" Abstract: {abstract}")

    # Example 2: Open access search
    print("\n\n2. Open Access Papers - Recent AI Research")
    papers = searcher.search(
        "artificial intelligence", 
        max_results=3,
        is_oa=True,
        from_publication_date="2023-01-01",
        sort="cited_by_count",
        order="desc"
    )
    
    for i, paper in enumerate(papers, 1):
        print(f"\n{i}. {paper.title}")
        print(f"   DOI: {paper.doi}")
        print(f"   PDF: {paper.pdf_url[:80]}{'...' if len(paper.pdf_url) > 80 else ''}")
        print(f"   Citations: {paper.citations}")
    
    # Example 3: Search by institution country
    print("\n\n3. Papers from German Institutions - Quantum Computing")
    papers = searcher.search(
        "quantum computing",
        max_results=3,
        institution_country="de",
        from_publication_date="2022-01-01"
    )
    
    for i, paper in enumerate(papers, 1):
        print(f"\n{i}. {paper.title}")
        print(f"   Authors: {', '.join(paper.authors[:2])}")
        print(f"   Categories: {', '.join(paper.categories[:3])}")
    
    # Example 4: Get specific paper by ID
    if papers:
        print("\n\n4. Get Paper by ID")
        paper_id = papers[0].paper_id
        paper = searcher.get_paper_by_id(paper_id)
        abstract = paper.abstract
        if paper:
            print(f"Retrieved: {paper.title}")
            if abstract:
                print(f"Abstract: {paper.abstract[:200]}...")
    
    # Example 5: Abstract search
    print("\n\n5. Abstract Search - Ethics in AI")
    papers = searcher.search(
        "",  # Empty main query
        max_results=3,
        abstract_search="machine learning ethics",
        has_abstract=True
    )
    
    for i, paper in enumerate(papers, 1):
        print(f"\n{i}. {paper.title}")
        abstract = paper.abstract
        if abstract:
            print(f"   Abstract snippet: {abstract[:150]}...")

if __name__ == "__main__":
    asyncio.run(main())