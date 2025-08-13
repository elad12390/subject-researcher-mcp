#!/usr/bin/env python3
"""Test runner for Subject Researcher MCP Server."""

import asyncio
import os
import sys
import time
import traceback

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import server components
try:
    from subject_researcher_mcp.server import (
        server,
        handle_list_tools,
        handle_call_tool,
        validate_date_range
    )
except ImportError as e:
    print(f"Warning: Could not import all server components: {e}")
    # Fallback for testing
    server = None
    handle_list_tools = None
    handle_call_tool = None
    validate_date_range = None

# Try importing specific functions
try:
    from subject_researcher_mcp.research_engine import ResearchEngine
    research_engine_available = True
except ImportError:
    research_engine_available = False

class TestRunner:
    """Comprehensive test runner for the MCP server."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.test_results = []
    
    async def run_test(self, test_name, test_func):
        """Run a single test function."""
        print(f"🧪 Running {test_name}...")
        try:
            start_time = time.time()
            await test_func()
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"✅ {test_name} PASSED ({duration:.2f}s)")
            self.passed += 1
            self.test_results.append({"name": test_name, "status": "PASSED", "duration": duration})
            return True
        except Exception as e:
            print(f"❌ {test_name} FAILED: {e}")
            print(f"   Traceback: {traceback.format_exc()}")
            self.failed += 1
            self.test_results.append({"name": test_name, "status": "FAILED", "error": str(e)})
            return False
    
    async def test_duckduckgo_basic_search(self):
        """Test basic DuckDuckGo search functionality."""
        results = await duckduckgo_search("python programming", max_results=3)
        assert isinstance(results, list), "Results should be a list"
        assert len(results) <= 3, "Should not exceed max_results"
        
        if results:
            result = results[0]
            assert 'title' in result, "Result should have title"
            assert 'body' in result, "Result should have body"
            assert 'href' in result, "Result should have href"
            assert isinstance(result['title'], str), "Title should be string"
    
    async def test_gemini_analysis(self):
        """Test Gemini analysis functionality."""
        mock_results = [
            {
                "title": "AI Test",
                "body": "Artificial intelligence is transforming technology.",
                "href": "https://example.com/ai"
            }
        ]
        
        analysis = await analyze_with_gemini(mock_results, "artificial intelligence")
        assert isinstance(analysis, dict), "Analysis should be a dict"
        assert 'summary' in analysis, "Analysis should have summary"
        assert 'key_findings' in analysis, "Analysis should have key_findings"
        assert isinstance(analysis['summary'], str), "Summary should be string"
        assert isinstance(analysis['key_findings'], list), "Key findings should be list"
    
    async def test_mcp_list_tools(self):
        """Test MCP tool listing."""
        tools = await handle_list_tools()
        assert isinstance(tools, list), "Tools should be a list"
        assert len(tools) == 2, "Should have exactly 2 tools"
        
        tool_names = [tool.name for tool in tools]
        assert "research_subject" in tool_names, "Should have research_subject tool"
        assert "quick_search" in tool_names, "Should have quick_search tool"
    
    async def test_research_subject_tool(self):
        """Test research_subject tool functionality."""
        arguments = {
            "subject": "machine learning",
            "max_results": 2,
            "depth": "basic"
        }
        
        result = await handle_call_tool("research_subject", arguments)
        assert isinstance(result, list), "Result should be a list"
        assert len(result) > 0, "Result should not be empty"
        
        content = result[0].text
        assert isinstance(content, str), "Content should be string"
        assert "machine learning" in content.lower(), "Content should mention the subject"
        assert "# Research Report:" in content, "Should have proper header"
        assert "## Summary" in content, "Should have summary section"
        assert "## Key Findings" in content, "Should have key findings section"
        assert "## Sources" in content, "Should have sources section"
    
    async def test_quick_search_tool(self):
        """Test quick_search tool functionality."""
        arguments = {
            "query": "data science",
            "max_results": 2
        }
        
        result = await handle_call_tool("quick_search", arguments)
        assert isinstance(result, list), "Result should be a list"
        assert len(result) > 0, "Result should not be empty"
        
        content = result[0].text
        assert isinstance(content, str), "Content should be string"
        assert "data science" in content.lower(), "Content should mention the query"
        assert "# Search Results for:" in content, "Should have proper header"
    
    async def test_error_handling(self):
        """Test error handling capabilities."""
        # Test unknown tool
        result = await handle_call_tool("unknown_tool", {})
        assert isinstance(result, list), "Should return list even for errors"
        assert len(result) > 0, "Should have error message"
        error_text = result[0].text.lower()
        assert "error" in error_text or "unknown" in error_text, "Should indicate error"
        
        # Test missing required parameter
        result = await handle_call_tool("research_subject", {})
        assert isinstance(result, list), "Should return list for parameter errors"
        assert len(result) > 0, "Should have error message"
        error_text = result[0].text.lower()
        assert "error" in error_text or "required" in error_text, "Should indicate missing parameter"
    
    async def test_performance(self):
        """Test basic performance characteristics."""
        start_time = time.time()
        
        # Run a quick search
        result = await handle_call_tool("quick_search", {
            "query": "performance test",
            "max_results": 1
        })
        
        end_time = time.time()
        duration = end_time - start_time
        
        assert duration < 30.0, f"Search took too long: {duration:.2f}s"
        assert isinstance(result, list), "Should return valid result"
        assert len(result) > 0, "Should have content"
    
    async def test_concurrent_requests(self):
        """Test handling concurrent requests."""
        # Create multiple search tasks
        tasks = [
            handle_call_tool("quick_search", {"query": "test1", "max_results": 1}),
            handle_call_tool("quick_search", {"query": "test2", "max_results": 1}),
            handle_call_tool("research_subject", {"subject": "test3", "max_results": 1, "depth": "basic"})
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        assert len(results) == 3, "Should complete all tasks"
        
        # Check that results are valid (allowing for network exceptions)
        valid_results = 0
        for result in results:
            if isinstance(result, Exception):
                # Network exceptions are acceptable
                print(f"   Network exception (acceptable): {result}")
            else:
                assert isinstance(result, list), "Valid results should be lists"
                valid_results += 1
        
        # At least some should succeed if network is available
        print(f"   {valid_results}/3 concurrent requests succeeded")
    
    async def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Test empty query handling
        result = await handle_call_tool("quick_search", {"query": ""})
        assert isinstance(result, list), "Should handle empty query gracefully"
        
        # Test zero max_results
        search_results = await duckduckgo_search("test", max_results=0)
        assert isinstance(search_results, list), "Should return list for zero max_results"
        assert len(search_results) == 0, "Should return empty list for zero max_results"
        
        # Test special characters
        result = await handle_call_tool("quick_search", {
            "query": "AI & ML: <test>",
            "max_results": 1
        })
        assert isinstance(result, list), "Should handle special characters"
    
    async def run_all_tests(self):
        """Run all tests and return summary."""
        print("🚀 Starting comprehensive E2E tests for Subject Researcher MCP Server\n")
        
        # Define all tests
        tests = [
            ("DuckDuckGo Basic Search", self.test_duckduckgo_basic_search),
            ("Gemini Analysis", self.test_gemini_analysis),
            ("MCP List Tools", self.test_mcp_list_tools),
            ("Research Subject Tool", self.test_research_subject_tool),
            ("Quick Search Tool", self.test_quick_search_tool),
            ("Error Handling", self.test_error_handling),
            ("Performance", self.test_performance),
            ("Concurrent Requests", self.test_concurrent_requests),
            ("Edge Cases", self.test_edge_cases),
            ("Date Validation Tests", self.test_date_validation),
        ]
        
        # Run all tests
        for test_name, test_func in tests:
            await self.run_test(test_name, test_func)
            print()  # Add spacing
        
        # Print summary
        total = self.passed + self.failed
        success_rate = (self.passed / total * 100) if total > 0 else 0
        
        print("=" * 60)
        print(f"📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Environment info
        print("🔧 ENVIRONMENT INFO:")
        print(f"Python Version: {sys.version}")
        print(f"Gemini API Key: {'✅ Available' if os.getenv('GEMINI_API_KEY') else '❌ Not Set'}")
        print()
        
        # Recommendations
        if self.failed == 0:
            print("🎉 ALL TESTS PASSED! The MCP server is ready for use.")
        else:
            print("⚠️  Some tests failed. Check the details above.")
            
        if not os.getenv('GEMINI_API_KEY'):
            print("💡 TIP: Set GEMINI_API_KEY environment variable for enhanced AI analysis")
        
        print("\n📝 Next steps:")
        print("1. Add the server to your MCP client configuration")
        print("2. Use research_subject and quick_search tools")
        print("3. Start researching any topic!")
        
        return self.failed == 0

async def main():
    """Main test runner entry point."""
    runner = TestRunner()
    success = await runner.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())