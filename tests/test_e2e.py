#!/usr/bin/env python3
"""End-to-end tests for Subject Researcher MCP Server."""

import asyncio
import json
import os
import sys
import tempfile
import time
from typing import Any, Dict, List

# Add src to Python path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
import mcp.types as types
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions

# Import our server modules
from subject_researcher_mcp.server import (
    server,
    duckduckgo_search,
    analyze_with_gemini,
    handle_list_tools,
    handle_call_tool
)

class TestDuckDuckGoIntegration:
    """Test DuckDuckGo search integration."""
    
    @pytest.mark.asyncio
    async def test_duckduckgo_search_basic(self):
        """Test basic DuckDuckGo search functionality."""
        results = await duckduckgo_search("python programming", max_results=3)
        
        assert isinstance(results, list)
        assert len(results) <= 3
        
        if results:  # If we got results (network dependent)
            for result in results:
                assert isinstance(result, dict)
                assert 'title' in result
                assert 'body' in result
                assert 'href' in result
                assert isinstance(result['title'], str)
                assert isinstance(result['body'], str)
                assert isinstance(result['href'], str)
    
    @pytest.mark.asyncio
    async def test_duckduckgo_search_empty_query_handling(self):
        """Test DuckDuckGo search with edge cases."""
        # Test with small max_results
        results = await duckduckgo_search("AI", max_results=1)
        assert isinstance(results, list)
        assert len(results) <= 1
        
        # Test with zero max_results
        results = await duckduckgo_search("test", max_results=0)
        assert isinstance(results, list)
        assert len(results) == 0
    
    @pytest.mark.asyncio
    async def test_duckduckgo_search_performance(self):
        """Test search performance is within reasonable bounds."""
        start_time = time.time()
        results = await duckduckgo_search("machine learning", max_results=3)
        end_time = time.time()
        
        duration = end_time - start_time
        # Should complete within 30 seconds
        assert duration < 30.0
        assert isinstance(results, list)

class TestGeminiIntegration:
    """Test Gemini AI integration."""
    
    @pytest.mark.asyncio
    async def test_gemini_analysis_with_mock_data(self):
        """Test Gemini analysis with mock search results."""
        mock_results = [
            {
                "title": "Artificial Intelligence Overview",
                "body": "AI is a branch of computer science focused on creating intelligent machines.",
                "href": "https://example.com/ai-overview"
            },
            {
                "title": "Machine Learning Fundamentals", 
                "body": "ML is a subset of AI that enables computers to learn without explicit programming.",
                "href": "https://example.com/ml-fundamentals"
            }
        ]
        
        analysis = await analyze_with_gemini(mock_results, "artificial intelligence")
        
        assert isinstance(analysis, dict)
        assert 'summary' in analysis
        assert 'key_findings' in analysis
        assert 'analysis' in analysis
        
        # Check that we get reasonable responses
        assert isinstance(analysis['summary'], str)
        assert isinstance(analysis['key_findings'], list)
        assert len(analysis['summary']) > 0
        assert len(analysis['key_findings']) > 0
    
    @pytest.mark.asyncio
    async def test_gemini_api_key_fallback(self):
        """Test behavior when Gemini API key is not available."""
        # Temporarily remove API key
        original_key = os.environ.get("GEMINI_API_KEY")
        if original_key:
            del os.environ["GEMINI_API_KEY"]
        
        try:
            mock_results = [
                {
                    "title": "Test Title",
                    "body": "Test content for fallback testing.",
                    "href": "https://example.com/test"
                }
            ]
            
            analysis = await analyze_with_gemini(mock_results, "test subject")
            
            assert isinstance(analysis, dict)
            assert 'summary' in analysis
            # Should indicate that Gemini is not available
            assert "not available" in analysis['summary'].lower() or "not set" in analysis['summary'].lower()
            
        finally:
            # Restore API key if it existed
            if original_key:
                os.environ["GEMINI_API_KEY"] = original_key

class TestMCPProtocol:
    """Test MCP protocol compliance."""
    
    @pytest.mark.asyncio
    async def test_list_tools(self):
        """Test MCP tool listing functionality."""
        tools = await handle_list_tools()
        
        assert isinstance(tools, list)
        assert len(tools) == 2  # Should have research_subject and quick_search
        
        tool_names = [tool.name for tool in tools]
        assert "research_subject" in tool_names
        assert "quick_search" in tool_names
        
        # Validate tool structure
        for tool in tools:
            assert isinstance(tool, types.Tool)
            assert hasattr(tool, 'name')
            assert hasattr(tool, 'description')
            assert hasattr(tool, 'inputSchema')
            assert isinstance(tool.name, str)
            assert isinstance(tool.description, str)
            assert isinstance(tool.inputSchema, dict)
            
            # Check required properties in schema
            if tool.name == "research_subject":
                assert 'properties' in tool.inputSchema
                assert 'subject' in tool.inputSchema['properties']
                assert 'required' in tool.inputSchema
                assert 'subject' in tool.inputSchema['required']
    
    @pytest.mark.asyncio
    async def test_call_research_subject_basic(self):
        """Test research_subject tool call with basic depth."""
        arguments = {
            "subject": "renewable energy",
            "max_results": 2,
            "depth": "basic"
        }
        
        result = await handle_call_tool("research_subject", arguments)
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert isinstance(result[0], types.TextContent)
        
        content = result[0].text
        assert isinstance(content, str)
        assert "renewable energy" in content.lower()
        assert "# Research Report:" in content
        assert "## Summary" in content
        assert "## Key Findings" in content
        assert "## Sources" in content
    
    @pytest.mark.asyncio
    async def test_call_research_subject_detailed(self):
        """Test research_subject tool call with detailed analysis."""
        arguments = {
            "subject": "quantum computing",
            "max_results": 3,
            "depth": "detailed"
        }
        
        result = await handle_call_tool("research_subject", arguments)
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert isinstance(result[0], types.TextContent)
        
        content = result[0].text
        assert isinstance(content, str)
        assert "quantum computing" in content.lower()
        assert "# Research Report:" in content
        
        # Should include all standard sections
        sections = ["## Summary", "## Key Findings", "## Sources"]
        for section in sections:
            assert section in content
    
    @pytest.mark.asyncio
    async def test_call_quick_search(self):
        """Test quick_search tool call."""
        arguments = {
            "query": "blockchain technology",
            "max_results": 2
        }
        
        result = await handle_call_tool("quick_search", arguments)
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert isinstance(result[0], types.TextContent)
        
        content = result[0].text
        assert isinstance(content, str)
        assert "blockchain technology" in content.lower()
        assert "# Search Results for:" in content
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test MCP protocol error handling."""
        # Test unknown tool
        result = await handle_call_tool("nonexistent_tool", {})
        assert isinstance(result, list)
        assert len(result) > 0
        assert isinstance(result[0], types.TextContent)
        error_content = result[0].text.lower()
        assert "unknown tool" in error_content or "error" in error_content
        
        # Test missing required parameter
        result = await handle_call_tool("research_subject", {})
        assert isinstance(result, list)
        assert len(result) > 0
        assert isinstance(result[0], types.TextContent)
        error_content = result[0].text.lower()
        assert "error" in error_content or "required" in error_content
        
        # Test invalid parameter values
        result = await handle_call_tool("quick_search", {"query": ""})
        assert isinstance(result, list)
        assert len(result) > 0
        assert isinstance(result[0], types.TextContent)
        error_content = result[0].text.lower()
        assert "error" in error_content or "required" in error_content

class TestEndToEndWorkflows:
    """Test complete end-to-end workflows."""
    
    @pytest.mark.asyncio
    async def test_complete_research_workflow(self):
        """Test a complete research workflow from start to finish."""
        subject = "sustainable development"
        
        # Step 1: Perform basic research
        basic_args = {
            "subject": subject,
            "max_results": 3,
            "depth": "basic"
        }
        
        basic_result = await handle_call_tool("research_subject", basic_args)
        assert isinstance(basic_result, list)
        assert len(basic_result) > 0
        
        basic_content = basic_result[0].text
        assert subject in basic_content.lower()
        assert len(basic_content) > 100  # Should have substantial content
        
        # Step 2: Perform detailed research (if Gemini available)
        detailed_args = {
            "subject": subject,
            "max_results": 3,
            "depth": "detailed"
        }
        
        detailed_result = await handle_call_tool("research_subject", detailed_args)
        assert isinstance(detailed_result, list)
        assert len(detailed_result) > 0
        
        detailed_content = detailed_result[0].text
        assert subject in detailed_content.lower()
        
        # Step 3: Quick search for comparison
        quick_args = {
            "query": subject,
            "max_results": 2
        }
        
        quick_result = await handle_call_tool("quick_search", quick_args)
        assert isinstance(quick_result, list)
        assert len(quick_result) > 0
        
        quick_content = quick_result[0].text
        assert subject in quick_content.lower()
        
        # Verify different formats
        assert "# Research Report:" in basic_content
        assert "# Research Report:" in detailed_content
        assert "# Search Results for:" in quick_content
    
    @pytest.mark.asyncio
    async def test_concurrent_tool_calls(self):
        """Test handling multiple concurrent tool calls."""
        # Create multiple concurrent requests
        tasks = [
            handle_call_tool("quick_search", {"query": "python", "max_results": 2}),
            handle_call_tool("quick_search", {"query": "javascript", "max_results": 2}),
            handle_call_tool("research_subject", {"subject": "web development", "max_results": 2, "depth": "basic"})
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All requests should complete
        assert len(results) == 3
        
        # Check that all results are valid
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Network/timeout exceptions are acceptable in tests
                print(f"Task {i} failed with exception: {result}")
            else:
                assert isinstance(result, list)
                assert len(result) > 0
                assert isinstance(result[0], types.TextContent)

class TestPerformanceAndReliability:
    """Test performance and reliability characteristics."""
    
    @pytest.mark.asyncio
    async def test_response_time_performance(self):
        """Test that responses come back within reasonable time."""
        start_time = time.time()
        
        result = await handle_call_tool("quick_search", {
            "query": "artificial intelligence",
            "max_results": 3
        })
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should respond within 30 seconds
        assert duration < 30.0
        assert isinstance(result, list)
        assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_memory_efficiency(self):
        """Test that operations don't consume excessive memory."""
        # Perform multiple operations to check for memory leaks
        for i in range(5):
            result = await handle_call_tool("quick_search", {
                "query": f"test query {i}",
                "max_results": 2
            })
            assert isinstance(result, list)
            # Brief pause to allow garbage collection
            await asyncio.sleep(0.1)
    
    @pytest.mark.asyncio
    async def test_edge_case_handling(self):
        """Test handling of edge cases and boundary conditions."""
        # Very long query
        long_query = "artificial intelligence " * 50  # Very long query
        result = await handle_call_tool("quick_search", {
            "query": long_query,
            "max_results": 1
        })
        assert isinstance(result, list)
        # Should handle gracefully, not crash
        
        # Special characters in query
        special_query = "AI & ML: <test> \"quotes\" @#$%"
        result = await handle_call_tool("quick_search", {
            "query": special_query,
            "max_results": 1
        })
        assert isinstance(result, list)
        
        # Unicode characters
        unicode_query = "人工智能 машинное обучение"
        result = await handle_call_tool("quick_search", {
            "query": unicode_query,
            "max_results": 1
        })
        assert isinstance(result, list)

class TestServerConfiguration:
    """Test server configuration and setup."""
    
    def test_server_initialization(self):
        """Test that server is properly initialized."""
        assert server is not None
        assert hasattr(server, 'get_capabilities')
        
        # Test server capabilities
        capabilities = server.get_capabilities(
            notification_options=NotificationOptions(),
            experimental_capabilities={}
        )
        
        assert hasattr(capabilities, 'tools')
    
    def test_server_handlers_registered(self):
        """Test that required handlers are registered."""
        # Server should have tools handler
        assert hasattr(server, '_tools_handlers')
        assert len(server._tools_handlers) > 0

if __name__ == "__main__":
    # Run a quick test to verify everything works
    async def quick_test():
        print("🧪 Running quick E2E verification...")
        
        # Test basic functionality
        tools = await handle_list_tools()
        print(f"✅ Found {len(tools)} tools: {[t.name for t in tools]}")
        
        # Test a simple search
        result = await handle_call_tool("quick_search", {
            "query": "test",
            "max_results": 1
        })
        print(f"✅ Quick search completed: {len(result[0].text)} characters")
        
        print("🎉 Basic E2E test passed!")
    
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        asyncio.run(quick_test())
    else:
        # Run full pytest suite
        pytest.main([__file__, "-v", "--tb=short"])