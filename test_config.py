#!/usr/bin/env python3
"""
Test OpenAlex configuration and basic functionality
"""

import os
import sys
from openalex_mcp.searcher import OpenAlexSearcher

def test_configuration():
    """Test OpenAlex configuration"""
    print("🧪 Testing OpenAlex MCP Server Configuration")
    print("=" * 50)
    
    # Check email configuration
    email = os.getenv('OPENALEX_EMAIL')
    api_key = os.getenv('OPENALEX_API_KEY')
    
    if email:
        print(f"✅ Email configured: {email}")
    else:
        print("⚠️  No email configured (OPENALEX_EMAIL)")
        print("   Set with: export OPENALEX_EMAIL=your.email@example.com")
    
    if api_key:
        print(f"✅ API key configured: {api_key[:8]}...")
    else:
        print("ℹ️  No API key configured (optional)")
    
    # Test basic functionality
    print(f"\n🔍 Testing basic search functionality...")
    
    try:
        searcher = OpenAlexSearcher(email=email, api_key=api_key)
        papers = searcher.search("machine learning", max_results=1)
        
        if papers:
            paper = papers[0]
            print("✅ Search successful!")
            print(f"   Sample result: {paper.title}")
            print(f"   Authors: {', '.join(paper.authors[:2])}")
            print(f"   Citations: {paper.citations}")
            print(f"   OpenAlex ID: {paper.paper_id}")
            
            # Test paper retrieval by ID
            print(f"\n🎯 Testing paper retrieval by ID...")
            retrieved_paper = searcher.get_paper_by_id(paper.paper_id)
            if retrieved_paper:
                print("✅ Paper retrieval by ID successful!")
            else:
                print("❌ Paper retrieval by ID failed")
                
        else:
            print("❌ No results returned (but connection works)")
            
    except Exception as e:
        print(f"❌ Error testing OpenAlex: {e}")
        return False
    
    print(f"\n🎉 Configuration test completed!")
    return True

def test_filters():
    """Test various filter combinations"""
    print(f"\n🔧 Testing filter functionality...")
    
    email = os.getenv('OPENALEX_EMAIL')
    searcher = OpenAlexSearcher(email=email)
    
    # Test date filter
    try:
        papers = searcher.search(
            "climate change", 
            max_results=2,
            from_publication_date="2023-01-01",
            is_oa=True
        )
        print(f"✅ Date + Open Access filter: {len(papers)} results")
        
    except Exception as e:
        print(f"❌ Filter test failed: {e}")
        return False
    
    # Test citation filter
    try:
        papers = searcher.search(
            "neural networks",
            max_results=2,
            cited_by_count=">100",
            sort="cited_by_count",
            order="desc"
        )
        print(f"✅ Citation filter: {len(papers)} results")
        
    except Exception as e:
        print(f"❌ Citation filter test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("OpenAlex MCP Server - Configuration Test\n")
    
    success = test_configuration()
    if success:
        success = test_filters()
    
    if success:
        print("\n🎉 All tests passed! Your OpenAlex MCP server is ready to use.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Check your configuration.")
        sys.exit(1)