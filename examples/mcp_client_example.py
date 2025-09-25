#!/usr/bin/env python3
"""
MCP Client Example
Demonstrates how to connect to the OpenAlex MCP server from a client.
"""

import asyncio
import json
from fastmcp import Client
from fastmcp.client import StdioTransport


async def main():
    """Example MCP client usage"""

    async with Client(StdioTransport("python3", ["-m", "openalex_mcp.server"])) as client:
        result = await client.list_tools()
        print("🛠️ Available Tools:")
        for tool in result:
            print(f"  - {tool.name}: {tool.description}")
        
        # Example 1: Basic search
        print("\n🔍 Example 1: Basic Search")
        result = await client.call_tool(
            "search_openalex",
            {
                "query": "machine learning",
                "max_results": 3
            }
        )
        
        papers = result.structured_content['result']
        for i, paper in enumerate(papers, 1):
            print(f"{i}. {paper.get('title', 'No title')}")
            print(f"   Authors: {paper.get('authors', 'N/A')}")
            print(f"   Citations: {paper.get('citations', 0)}")
            print(f"   Year: {paper.get('published_date', 'N/A')[:4]}")
            print()
        
        # Example 2: Open access search
        print("\n🔓 Example 2: Open Access Papers")
        result = await client.call_tool(
            "search_open_access_papers",
            {
                "query": "climate change",
                "max_results": 2,
                "from_publication_date": "2023-01-01"
            }
        )
        
        papers = result.structured_content['result']
        for paper in papers:
            print(f"- {paper.get('title', 'No title')}")
            print(f"  DOI: {paper.get('doi', 'No DOI')}")
            print(f"  Open Access: Yes")
            print()
        
        # Example 3: Get specific paper
        if papers:
            print("\n📄 Example 3: Get Paper by ID")
            first_paper_id = papers[0].get('paper_id', '')
            if first_paper_id:
                result = await client.call_tool(
                    "get_paper_by_id",
                    {"openalex_id": first_paper_id}
                )
                
                if hasattr(result, 'structured_content') and result.structured_content:
                    paper_details = result.structured_content.get('result', {})
                else:
                    # Fallback to content
                    paper_details = json.loads(result.content[0].text) if result.content else {}
                    
                if paper_details:
                    print(f"Title: {paper_details.get('title', 'No title')}")
                    print(f"Authors: {paper_details.get('authors', 'No authors')}")
                    print(f"Abstract: {paper_details.get('abstract', 'No abstract')[:200]}...")
                else:
                    print("No paper details found")

if __name__ == "__main__":
    asyncio.run(main())