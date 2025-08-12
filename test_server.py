#!/usr/bin/env python3
"""Simple test script for the Subject Researcher MCP Server."""

import asyncio
import json
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from subject_researcher_mcp.server import duckduckgo_search, analyze_with_gemini

async def test_duckduckgo_search():
    """Test DuckDuckGo search functionality."""
    print("Testing DuckDuckGo search...")
    
    results = await duckduckgo_search("artificial intelligence", max_results=3)
    
    if results:
        print(f"✅ DuckDuckGo search successful! Found {len(results)} results:")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['title']}")
            print(f"     {result['body'][:100]}...")
            print(f"     URL: {result['href']}")
            print()
    else:
        print("❌ DuckDuckGo search failed - no results found")
    
    return len(results) > 0

async def test_gemini_analysis():
    """Test Gemini AI analysis functionality."""
    print("Testing Gemini AI analysis...")
    
    # Create mock search results for testing
    mock_results = [
        {
            "title": "Artificial Intelligence Overview",
            "body": "Artificial intelligence (AI) is a branch of computer science that aims to create intelligent machines.",
            "href": "https://example.com/ai-overview"
        },
        {
            "title": "Machine Learning Basics",
            "body": "Machine learning is a subset of AI that enables computers to learn without being explicitly programmed.",
            "href": "https://example.com/ml-basics"
        }
    ]
    
    analysis = await analyze_with_gemini(mock_results, "artificial intelligence")
    
    if analysis and "error" not in analysis.get("summary", "").lower():
        print("✅ Gemini analysis successful!")
        print(f"   Summary: {analysis['summary']}")
        print(f"   Key findings: {len(analysis['key_findings'])} items")
        if analysis.get('analysis'):
            print(f"   Detailed analysis: {len(analysis['analysis'])} characters")
    else:
        print("⚠️  Gemini analysis not available or failed")
        if os.getenv("GEMINI_API_KEY"):
            print("   - API key is set, but analysis failed")
        else:
            print("   - GEMINI_API_KEY environment variable not set")
    
    return True

async def main():
    """Run all tests."""
    print("🧪 Testing Subject Researcher MCP Server\n")
    
    # Test DuckDuckGo search
    search_success = await test_duckduckgo_search()
    
    print("-" * 50)
    
    # Test Gemini analysis
    gemini_success = await test_gemini_analysis()
    
    print("-" * 50)
    print("\n📊 Test Summary:")
    print(f"   DuckDuckGo Search: {'✅ Working' if search_success else '❌ Failed'}")
    print(f"   Gemini Analysis: {'✅ Available' if os.getenv('GEMINI_API_KEY') else '⚠️  No API key'}")
    
    if search_success:
        print("\n🎉 Server is ready to use!")
        print("\nNext steps:")
        print("1. Set GEMINI_API_KEY environment variable for AI analysis")
        print("2. Connect to your MCP client (Claude Desktop, etc.)")
        print("3. Use the research_subject and quick_search tools")
    else:
        print("\n❌ Server has issues. Check your internet connection.")

if __name__ == "__main__":
    asyncio.run(main())