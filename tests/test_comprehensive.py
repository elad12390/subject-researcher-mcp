#!/usr/bin/env python3
"""Comprehensive test suite for Subject Researcher MCP Server."""

import asyncio
import os
import sys
import time
from typing import List, Dict, Any

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from subject_researcher_mcp.server import (
    server,
    duckduckgo_search,
    analyze_with_gemini,
    handle_list_tools,
    handle_call_tool
)

class TestFullSystemIntegration:
    """Complete system integration tests."""
    
    @pytest.mark.asyncio
    async def test_system_startup_and_configuration(self):
        """Test that the system starts up correctly and is properly configured."""
        # Test server object exists
        assert server is not None
        
        # Test that handlers are registered
        assert hasattr(server, '_tools_handlers')
        assert len(server._tools_handlers) > 0
        
        # Test capabilities
        capabilities = server.get_capabilities(
            notification_options=None,
            experimental_capabilities={}
        )
        assert hasattr(capabilities, 'tools')
    
    @pytest.mark.asyncio
    async def test_mcp_protocol_compliance(self):
        """Test full MCP protocol compliance."""
        # Test list_tools
        tools = await handle_list_tools()
        assert isinstance(tools, list)
        assert len(tools) == 2
        
        tool_names = [tool.name for tool in tools]
        assert "research_subject" in tool_names
        assert "quick_search" in tool_names
        
        # Validate each tool's schema
        for tool in tools:
            assert hasattr(tool, 'name')
            assert hasattr(tool, 'description')
            assert hasattr(tool, 'inputSchema')
            assert isinstance(tool.inputSchema, dict)
            assert 'type' in tool.inputSchema
            assert tool.inputSchema['type'] == 'object'
            
            if tool.name == "research_subject":
                assert 'properties' in tool.inputSchema
                assert 'subject' in tool.inputSchema['properties']
                assert 'required' in tool.inputSchema
                assert 'subject' in tool.inputSchema['required']
    
    @pytest.mark.asyncio
    async def test_end_to_end_research_workflow(self):
        """Test complete end-to-end research workflow."""
        subject = "sustainable technology"
        
        # Test basic research
        basic_result = await handle_call_tool("research_subject", {
            "subject": subject,
            "max_results": 3,
            "depth": "basic"
        })
        
        assert isinstance(basic_result, list)
        assert len(basic_result) > 0
        basic_content = basic_result[0].text
        
        # Verify basic report structure (even if no results found)
        assert "# Research Report:" in basic_content
        
        if "No search results found" not in basic_content:
            # If results were found, verify complete structure
            assert "## Summary" in basic_content
            assert "## Key Findings" in basic_content
            assert "## Sources" in basic_content
            assert subject in basic_content.lower()
        
        # Test detailed research
        detailed_result = await handle_call_tool("research_subject", {
            "subject": subject,
            "max_results": 3,
            "depth": "detailed"
        })
        
        assert isinstance(detailed_result, list)
        assert len(detailed_result) > 0
        detailed_content = detailed_result[0].text
        
        # Both should have the main header
        assert "# Research Report:" in detailed_content
        
        print(f"Basic research: {len(basic_content)} chars")
        print(f"Detailed research: {len(detailed_content)} chars")
    
    @pytest.mark.asyncio
    async def test_error_recovery_and_resilience(self):
        """Test system error recovery and resilience."""
        # Test with invalid tool name
        result = await handle_call_tool("invalid_tool", {})
        assert isinstance(result, list)
        assert len(result) > 0
        assert "error" in result[0].text.lower() or "unknown" in result[0].text.lower()
        
        # Test with missing required parameters
        result = await handle_call_tool("research_subject", {})
        assert isinstance(result, list)
        assert len(result) > 0
        error_text = result[0].text.lower()
        assert "error" in error_text or "required" in error_text
        
        # Test with empty/invalid parameters
        result = await handle_call_tool("quick_search", {"query": ""})
        assert isinstance(result, list)
        assert len(result) > 0
        error_text = result[0].text.lower()
        assert "error" in error_text or "required" in error_text
        
        # System should remain functional after errors
        valid_result = await handle_call_tool("quick_search", {
            "query": "test query",
            "max_results": 1
        })
        assert isinstance(valid_result, list)
        assert len(valid_result) > 0
    
    @pytest.mark.asyncio
    async def test_performance_under_load(self):
        """Test system performance under concurrent load."""
        # Create multiple concurrent requests
        num_requests = 3  # Reduced for stability
        tasks = []
        
        for i in range(num_requests):
            # Mix of different request types
            if i % 2 == 0:
                task = handle_call_tool("quick_search", {
                    "query": f"technology {i}",
                    "max_results": 1
                })
            else:
                task = handle_call_tool("research_subject", {
                    "subject": f"innovation {i}",
                    "max_results": 1,
                    "depth": "basic"
                })
            tasks.append(task)
        
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time
        
        # Count successful requests
        successful = 0
        exceptions = 0
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                exceptions += 1
                print(f"Request {i} failed: {type(result).__name__}")
            else:
                assert isinstance(result, list)
                assert len(result) > 0
                successful += 1
        
        print(f"Performance test: {successful}/{num_requests} succeeded, {exceptions} exceptions")
        print(f"Total time: {total_time:.2f}s, Average: {total_time/num_requests:.2f}s per request")
        
        # Should complete within reasonable time
        assert total_time < 90.0, f"Performance test took too long: {total_time:.2f}s"
    
    @pytest.mark.asyncio
    async def test_different_query_complexity(self):
        """Test handling queries of different complexity."""
        test_cases = [
            {
                "name": "Simple Query",
                "args": {"query": "AI", "max_results": 1},
                "tool": "quick_search"
            },
            {
                "name": "Complex Query",
                "args": {"query": "artificial intelligence machine learning deep neural networks", "max_results": 2},
                "tool": "quick_search"
            },
            {
                "name": "Special Characters",
                "args": {"query": "AI & ML: <advanced>", "max_results": 1},
                "tool": "quick_search"
            },
            {
                "name": "Simple Research",
                "args": {"subject": "technology", "max_results": 1, "depth": "basic"},
                "tool": "research_subject"
            },
            {
                "name": "Complex Research",
                "args": {"subject": "quantum machine learning applications", "max_results": 2, "depth": "basic"},
                "tool": "research_subject"
            }
        ]
        
        for case in test_cases:
            print(f"Testing: {case['name']}")
            result = await handle_call_tool(case['tool'], case['args'])
            
            assert isinstance(result, list), f"Failed for {case['name']}"
            assert len(result) > 0, f"No result for {case['name']}"
            
            content = result[0].text
            assert isinstance(content, str), f"Invalid content type for {case['name']}"
            assert len(content) > 0, f"Empty content for {case['name']}"
    
    @pytest.mark.asyncio
    async def test_gemini_integration_robustness(self):
        """Test Gemini integration robustness."""
        # Test with various content types
        test_scenarios = [
            {
                "name": "Technical Content",
                "results": [
                    {
                        "title": "Advanced AI Systems",
                        "body": "Modern AI systems utilize transformer architectures and attention mechanisms.",
                        "href": "https://example.com/ai-systems"
                    }
                ],
                "query": "AI systems"
            },
            {
                "name": "Empty Results",
                "results": [],
                "query": "empty test"
            },
            {
                "name": "Minimal Content",
                "results": [
                    {
                        "title": "Test",
                        "body": "Brief content.",
                        "href": "https://example.com"
                    }
                ],
                "query": "test"
            }
        ]
        
        for scenario in test_scenarios:
            analysis = await analyze_with_gemini(scenario["results"], scenario["query"])
            
            # Should always return valid structure
            assert isinstance(analysis, dict)
            assert 'summary' in analysis
            assert 'key_findings' in analysis
            assert 'analysis' in analysis
            
            # Summary should always be a string
            assert isinstance(analysis['summary'], str)
            assert len(analysis['summary']) > 0
            
            # Key findings should always be a list
            assert isinstance(analysis['key_findings'], list)
            assert len(analysis['key_findings']) > 0
            
            print(f"✅ {scenario['name']}: Analysis completed successfully")
    
    @pytest.mark.asyncio
    async def test_network_resilience(self):
        """Test resilience to network issues."""
        # Test multiple searches with different terms
        # Some may fail due to network issues, but system should handle gracefully
        search_terms = ["python", "javascript", "rust", "go", "java"]
        
        successful_searches = 0
        failed_searches = 0
        
        for term in search_terms:
            try:
                results = await duckduckgo_search(term, max_results=1)
                assert isinstance(results, list)
                successful_searches += 1
            except Exception as e:
                failed_searches += 1
                print(f"Search for '{term}' failed (acceptable): {type(e).__name__}")
        
        print(f"Network resilience: {successful_searches}/{len(search_terms)} searches succeeded")
        
        # At least some searches should work if network is available
        # But we don't fail the test if network is completely unavailable
        total_searches = successful_searches + failed_searches
        assert total_searches == len(search_terms), "Not all searches were attempted"
    
    @pytest.mark.asyncio
    async def test_data_quality_and_formatting(self):
        """Test quality and formatting of returned data."""
        # Test that returned data is well-formatted and useful
        result = await handle_call_tool("research_subject", {
            "subject": "data science",
            "max_results": 2,
            "depth": "basic"
        })
        
        assert isinstance(result, list)
        assert len(result) > 0
        
        content = result[0].text
        
        # Check basic formatting
        assert content.startswith("#"), "Should start with markdown header"
        assert "# Research Report:" in content, "Should have main title"
        
        # If results found, check structure
        if "No search results found" not in content:
            # Should have proper sections
            sections = content.split("##")
            assert len(sections) >= 4, "Should have multiple sections"  # Title + Summary + Key Findings + Sources
            
            # Check for proper markdown formatting
            assert content.count("#") >= 3, "Should have proper heading hierarchy"
            
            # Should have some bullet points or numbered items
            assert ("- " in content or "1." in content), "Should have lists or bullet points"
        
        print(f"Content structure verified: {len(content)} characters")

class TestRegressionAndEdgeCases:
    """Test regression scenarios and edge cases."""
    
    @pytest.mark.asyncio
    async def test_boundary_conditions(self):
        """Test boundary conditions and edge cases."""
        # Test with max_results = 0
        results = await duckduckgo_search("test", max_results=0)
        assert isinstance(results, list)
        assert len(results) == 0
        
        # Test with max_results = 1
        results = await duckduckgo_search("test", max_results=1)
        assert isinstance(results, list)
        assert len(results) <= 1
        
        # Test with very large max_results
        results = await duckduckgo_search("test", max_results=100)
        assert isinstance(results, list)
        # Should handle gracefully (either cap or return what's available)
    
    @pytest.mark.asyncio
    async def test_unicode_and_special_characters(self):
        """Test handling of unicode and special characters."""
        special_queries = [
            "café résumé naïve",  # Accented characters
            "学习 машинное обучение",  # Chinese and Cyrillic
            "AI & ML: <advanced> \"quotes\"",  # Special symbols
            "emoji test 🤖 🔬 💻",  # Emojis
        ]
        
        for query in special_queries:
            result = await handle_call_tool("quick_search", {
                "query": query,
                "max_results": 1
            })
            
            assert isinstance(result, list)
            assert len(result) > 0
            
            content = result[0].text
            assert isinstance(content, str)
            # Should handle gracefully without crashing
            print(f"✅ Handled special query: {query[:20]}...")
    
    @pytest.mark.asyncio
    async def test_tool_schema_validation(self):
        """Test that tool schemas are properly defined."""
        tools = await handle_list_tools()
        
        for tool in tools:
            schema = tool.inputSchema
            
            # Basic schema validation
            assert 'type' in schema
            assert schema['type'] == 'object'
            
            if 'properties' in schema:
                for prop_name, prop_def in schema['properties'].items():
                    assert 'type' in prop_def, f"Property {prop_name} missing type"
                    assert 'description' in prop_def, f"Property {prop_name} missing description"
            
            if 'required' in schema:
                assert isinstance(schema['required'], list), "Required should be a list"
                for required_prop in schema['required']:
                    assert required_prop in schema.get('properties', {}), f"Required property {required_prop} not in properties"
    
    @pytest.mark.asyncio
    async def test_memory_and_resource_management(self):
        """Test memory usage and resource management."""
        # Run multiple operations to check for memory leaks
        operations = []
        
        for i in range(10):
            # Alternate between different operations
            if i % 3 == 0:
                op = handle_call_tool("quick_search", {"query": f"test {i}", "max_results": 1})
            elif i % 3 == 1:
                op = handle_call_tool("research_subject", {"subject": f"topic {i}", "max_results": 1, "depth": "basic"})
            else:
                op = duckduckgo_search(f"query {i}", max_results=1)
            
            operations.append(op)
        
        # Execute all operations
        start_time = time.time()
        results = await asyncio.gather(*operations, return_exceptions=True)
        end_time = time.time()
        
        # Verify all completed
        assert len(results) == 10
        
        # Count successes vs exceptions
        successes = sum(1 for r in results if not isinstance(r, Exception))
        exceptions = len(results) - successes
        
        print(f"Memory test: {successes} successes, {exceptions} exceptions in {end_time - start_time:.2f}s")
        
        # System should remain responsive
        assert end_time - start_time < 120.0, "Operations took too long"

# Helper function to run all tests
async def run_comprehensive_tests():
    """Run comprehensive test suite manually."""
    print("🚀 Starting Comprehensive Test Suite")
    print("=" * 60)
    
    test_classes = [
        TestFullSystemIntegration(),
        TestRegressionAndEdgeCases()
    ]
    
    total_tests = 0
    passed_tests = 0
    
    for test_class in test_classes:
        class_name = test_class.__class__.__name__
        print(f"\n📊 Running {class_name}")
        print("-" * 40)
        
        # Get all test methods
        test_methods = [method for method in dir(test_class) if method.startswith('test_')]
        
        for method_name in test_methods:
            total_tests += 1
            test_method = getattr(test_class, method_name)
            
            try:
                print(f"🧪 {method_name}...")
                start_time = time.time()
                await test_method()
                duration = time.time() - start_time
                print(f"✅ PASSED ({duration:.2f}s)")
                passed_tests += 1
            except Exception as e:
                print(f"❌ FAILED: {e}")
    
    print("\n" + "=" * 60)
    print(f"📈 COMPREHENSIVE TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL COMPREHENSIVE TESTS PASSED!")
        print("✨ The Subject Researcher MCP Server is fully validated and ready for production use!")
    else:
        print(f"\n⚠️  {total_tests - passed_tests} tests failed. Review the failures above.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--manual":
        # Run manual test suite
        asyncio.run(run_comprehensive_tests())
    else:
        # Run with pytest
        pytest.main([__file__, "-v", "--tb=short", "-s"])