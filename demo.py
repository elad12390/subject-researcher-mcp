#!/usr/bin/env python3
"""Demo script showing how the Subject Researcher MCP Server works."""

import asyncio
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from subject_researcher_mcp.server import duckduckgo_search, analyze_with_gemini

async def demo_basic_research():
    """Demo basic research functionality."""
    print("🔍 Demo: Basic Research on 'Quantum Computing'\n")
    
    # Search for information
    results = await duckduckgo_search("quantum computing", max_results=5)
    
    if not results:
        print("❌ No search results found")
        return
    
    # Generate basic report
    print("# Research Report: Quantum Computing\n")
    print(f"## Summary\nFound {len(results)} results about quantum computing\n")
    print("## Key Findings")
    for result in results[:5]:
        print(f"- {result['title']}")
    print()
    
    print("## Sources")
    for i, result in enumerate(results, 1):
        if result['href']:
            print(f"{i}. [{result['title']}]({result['href']})")
        else:
            print(f"{i}. {result['title']}")
    
    print("\n" + "="*60 + "\n")

async def demo_detailed_research():
    """Demo detailed research with AI analysis."""
    print("🧠 Demo: Detailed Research with AI Analysis\n")
    
    # Search for information
    results = await duckduckgo_search("blockchain technology", max_results=3)
    
    if not results:
        print("❌ No search results found")
        return
    
    print("Search results found:")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['title']}")
    print()
    
    # Analyze with Gemini (will show appropriate message if no API key)
    analysis = await analyze_with_gemini(results, "blockchain technology")
    
    print("# Research Report: Blockchain Technology\n")
    print(f"## Summary\n{analysis['summary']}\n")
    print("## Key Findings")
    for finding in analysis['key_findings']:
        print(f"- {finding}")
    print()
    
    if analysis.get('analysis'):
        print(f"## Detailed Analysis\n{analysis['analysis'][:200]}...\n")
    
    print("## Sources")
    for i, result in enumerate(results, 1):
        if result['href']:
            print(f"{i}. [{result['title']}]({result['href']})")
        else:
            print(f"{i}. {result['title']}")
    
    print("\n" + "="*60 + "\n")

async def main():
    """Run the demo."""
    print("🚀 Subject Researcher MCP Server Demo\n")
    print("This demo shows how the MCP server tools work:\n")
    
    await demo_basic_research()
    await demo_detailed_research()
    
    print("✨ Demo Complete!\n")
    print("To use this server:")
    print("1. Add the server to your MCP client configuration")
    print("2. Use the 'research_subject' tool for comprehensive research")
    print("3. Use the 'quick_search' tool for simple searches")
    print("4. Set GEMINI_API_KEY for enhanced AI analysis")

if __name__ == "__main__":
    asyncio.run(main())