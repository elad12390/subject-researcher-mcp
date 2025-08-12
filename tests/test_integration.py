#!/usr/bin/env python3
"""Integration tests for Subject Researcher MCP Server."""

import asyncio
import os
import sys
import time
from typing import Dict, List

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from subject_researcher_mcp.server import (
    duckduckgo_search,
    analyze_with_gemini,
    handle_list_tools,
    handle_call_tool
)

class TestIntegrationWorkflows:
    """Test complete integration workflows."""
    
    @pytest.mark.asyncio
    async def test_complete_research_workflow_basic(self):
        """Test complete basic research workflow."""
        subject = "renewable energy"
        
        # Step 1: Test direct search
        search_results = await duckduckgo_search(subject, max_results=3)
        assert isinstance(search_results, list)
        
        # Step 2: Test tool call
        arguments = {
            "subject": subject,
            "max_results": 3,
            "depth": "basic"
        }
        
        result = await handle_call_tool("research_subject", arguments)
        assert isinstance(result, list)
        assert len(result) > 0
        
        content = result[0].text
        assert subject in content.lower()
        
        # Verify report structure
        required_sections = ["# Research Report:", "## Summary", "## Key Findings", "## Sources"]
        for section in required_sections:
            assert section in content, f"Missing section: {section}"
        
        # Verify content quality
        assert len(content) > 200, "Report should have substantial content"
        assert content.count("##") >= 3, "Should have at least 3 sections"
    
    @pytest.mark.asyncio
    async def test_complete_research_workflow_detailed(self):
        """Test complete detailed research workflow with AI analysis."""
        subject = "artificial intelligence ethics"
        
        arguments = {
            "subject": subject,
            "max_results": 4,
            "depth": "detailed"
        }
        
        result = await handle_call_tool("research_subject", arguments)
        assert isinstance(result, list)
        assert len(result) > 0
        
        content = result[0].text
        assert subject in content.lower()
        
        # Should have all standard sections
        required_sections = ["# Research Report:", "## Summary", "## Key Findings", "## Sources"]
        for section in required_sections:
            assert section in content
        
        # If Gemini is available, should have enhanced content
        if os.getenv("GEMINI_API_KEY"):
            # Should have more detailed analysis
            assert len(content) > 400, "Detailed analysis should be longer"
        else:
            # Should still work with basic analysis
            assert len(content) > 200, "Should have basic content"
    
    @pytest.mark.asyncio
    async def test_quick_search_workflow(self):
        """Test quick search workflow."""
        query = "machine learning algorithms"
        
        arguments = {
            "query": query,
            "max_results": 3
        }
        
        result = await handle_call_tool("quick_search", arguments)
        assert isinstance(result, list)
        assert len(result) > 0
        
        content = result[0].text
        assert query in content.lower()
        assert "# Search Results for:" in content
        
        # Should have numbered results if any found
        if "No search results found" not in content:
            assert "1." in content, "Should have numbered results"
    
    @pytest.mark.asyncio
    async def test_comparative_analysis(self):
        """Test comparing basic vs detailed research outputs."""
        subject = "quantum computing"
        
        # Basic research
        basic_args = {
            "subject": subject,
            "max_results": 3,
            "depth": "basic"
        }
        basic_result = await handle_call_tool("research_subject", basic_args)
        basic_content = basic_result[0].text
        
        # Detailed research
        detailed_args = {
            "subject": subject,
            "max_results": 3,
            "depth": "detailed"
        }
        detailed_result = await handle_call_tool("research_subject", detailed_args)
        detailed_content = detailed_result[0].text
        
        # Both should be valid reports
        for content in [basic_content, detailed_content]:
            assert "# Research Report:" in content
            assert "## Summary" in content
            assert "## Key Findings" in content
            assert "## Sources" in content
        
        # Both should mention the subject
        assert subject in basic_content.lower()
        assert subject in detailed_content.lower()
        
        print(f"Basic report length: {len(basic_content)} characters")
        print(f"Detailed report length: {len(detailed_content)} characters")
    
    @pytest.mark.asyncio
    async def test_different_subject_domains(self):
        """Test research across different subject domains."""
        subjects = [
            "climate change",
            "blockchain technology",
            "space exploration",
            "biotechnology"
        ]
        
        for subject in subjects:
            arguments = {
                "subject": subject,
                "max_results": 2,
                "depth": "basic"
            }
            
            result = await handle_call_tool("research_subject", arguments)
            assert isinstance(result, list)
            assert len(result) > 0
            
            content = result[0].text
            assert subject in content.lower()
            assert "# Research Report:" in content
            
            # Each domain should produce valid research
            assert len(content) > 100, f"Insufficient content for {subject}"
    
    @pytest.mark.asyncio
    async def test_search_result_consistency(self):
        """Test that search results are consistent and well-formatted."""
        # Test multiple searches
        queries = ["python programming", "data analysis", "web development"]
        
        for query in queries:
            results = await duckduckgo_search(query, max_results=3)
            assert isinstance(results, list)
            
            # If results found, verify structure
            for result in results:
                if result:  # Skip empty results
                    assert isinstance(result, dict)
                    assert 'title' in result
                    assert 'body' in result
                    assert 'href' in result
                    
                    # Verify types
                    assert isinstance(result['title'], str)
                    assert isinstance(result['body'], str)
                    assert isinstance(result['href'], str)
    
    @pytest.mark.asyncio
    async def test_tool_parameter_validation(self):
        """Test tool parameter validation and edge cases."""
        # Test research_subject with different parameters
        test_cases = [
            {
                "args": {"subject": "AI", "max_results": 1, "depth": "basic"},
                "should_work": True
            },
            {
                "args": {"subject": "AI", "max_results": 0, "depth": "basic"},
                "should_work": True  # Should handle gracefully
            },
            {
                "args": {"subject": "AI", "max_results": 50, "depth": "basic"},
                "should_work": True  # Should cap or handle large numbers
            },
            {
                "args": {"subject": "AI", "depth": "comprehensive"},
                "should_work": True  # max_results is optional
            },
            {
                "args": {"max_results": 5, "depth": "basic"},
                "should_work": False  # subject is required
            },
        ]
        
        for i, test_case in enumerate(test_cases):
            result = await handle_call_tool("research_subject", test_case["args"])
            assert isinstance(result, list)
            assert len(result) > 0
            
            if test_case["should_work"]:
                # Should not be an error message
                assert not ("error" in result[0].text.lower() and "required" in result[0].text.lower())
            else:
                # Should be an error message
                assert "error" in result[0].text.lower() or "required" in result[0].text.lower()

class TestGeminiIntegration:
    """Test Gemini AI integration specifically."""
    
    @pytest.mark.asyncio
    async def test_gemini_analysis_structure(self):
        """Test Gemini analysis output structure."""
        mock_results = [
            {
                "title": "Artificial Intelligence in Healthcare",
                "body": "AI is revolutionizing medical diagnosis and treatment planning through machine learning algorithms.",
                "href": "https://example.com/ai-healthcare"
            },
            {
                "title": "Ethics of AI Development",
                "body": "As AI systems become more prevalent, ethical considerations around bias, privacy, and transparency are crucial.",
                "href": "https://example.com/ai-ethics"
            }
        ]
        
        analysis = await analyze_with_gemini(mock_results, "AI in healthcare and ethics")
        
        # Should always return a dict with required keys
        assert isinstance(analysis, dict)
        required_keys = ['summary', 'key_findings', 'analysis']
        for key in required_keys:
            assert key in analysis, f"Missing key: {key}"
        
        # Check types
        assert isinstance(analysis['summary'], str)
        assert isinstance(analysis['key_findings'], list)
        # analysis can be None if no detailed analysis is provided
        
        # Summary should have content
        assert len(analysis['summary']) > 0
        assert len(analysis['key_findings']) > 0
    
    @pytest.mark.asyncio
    async def test_gemini_with_different_content_types(self):
        """Test Gemini analysis with different types of content."""
        test_scenarios = [
            {
                "name": "Technical Content",
                "results": [
                    {
                        "title": "Machine Learning Algorithms",
                        "body": "Deep learning networks use backpropagation for training neural networks.",
                        "href": "https://example.com/ml"
                    }
                ],
                "query": "machine learning algorithms"
            },
            {
                "name": "News Content",
                "results": [
                    {
                        "title": "Technology News Update",
                        "body": "Latest developments in the tech industry show rapid growth in AI adoption.",
                        "href": "https://example.com/news"
                    }
                ],
                "query": "technology news"
            },
            {
                "name": "Academic Content",
                "results": [
                    {
                        "title": "Research Paper on Climate Change",
                        "body": "Studies indicate significant correlation between industrial emissions and global warming.",
                        "href": "https://example.com/research"
                    }
                ],
                "query": "climate change research"
            }
        ]
        
        for scenario in test_scenarios:
            analysis = await analyze_with_gemini(scenario["results"], scenario["query"])
            
            # Should handle all content types properly
            assert isinstance(analysis, dict)
            assert len(analysis['summary']) > 0
            assert isinstance(analysis['key_findings'], list)
            
            print(f"✅ {scenario['name']}: {len(analysis['summary'])} char summary")

class TestPerformanceAndScalability:
    """Test performance and scalability characteristics."""
    
    @pytest.mark.asyncio
    async def test_response_time_benchmarks(self):
        """Test response times for different operations."""
        benchmarks = {}
        
        # Quick search benchmark
        start_time = time.time()
        await handle_call_tool("quick_search", {"query": "test", "max_results": 2})
        benchmarks["quick_search"] = time.time() - start_time
        
        # Basic research benchmark
        start_time = time.time()
        await handle_call_tool("research_subject", {
            "subject": "test topic",
            "max_results": 2,
            "depth": "basic"
        })
        benchmarks["basic_research"] = time.time() - start_time
        
        # Detailed research benchmark (if Gemini available)
        start_time = time.time()
        await handle_call_tool("research_subject", {
            "subject": "test topic",
            "max_results": 2,
            "depth": "detailed"
        })
        benchmarks["detailed_research"] = time.time() - start_time
        
        # Print benchmark results
        print("\n⏱️  Performance Benchmarks:")
        for operation, duration in benchmarks.items():
            print(f"   {operation}: {duration:.2f}s")
        
        # Verify reasonable performance
        assert benchmarks["quick_search"] < 30.0, "Quick search too slow"
        assert benchmarks["basic_research"] < 30.0, "Basic research too slow"
        assert benchmarks["detailed_research"] < 60.0, "Detailed research too slow"
    
    @pytest.mark.asyncio
    async def test_concurrent_load(self):
        """Test handling concurrent requests under load."""
        num_concurrent = 5
        
        # Create multiple concurrent research requests
        tasks = []
        for i in range(num_concurrent):
            task = handle_call_tool("research_subject", {
                "subject": f"technology trends {i}",
                "max_results": 2,
                "depth": "basic"
            })
            tasks.append(task)
        
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_duration = time.time() - start_time
        
        # Count successful requests
        successful = 0
        for result in results:
            if isinstance(result, Exception):
                print(f"   Exception (acceptable): {type(result).__name__}")
            else:
                assert isinstance(result, list)
                assert len(result) > 0
                successful += 1
        
        print(f"   {successful}/{num_concurrent} concurrent requests succeeded")
        print(f"   Total time: {total_duration:.2f}s")
        print(f"   Average per request: {total_duration/num_concurrent:.2f}s")
        
        # Should handle reasonable load
        assert total_duration < 120.0, "Concurrent load took too long"

if __name__ == "__main__":
    # Run integration tests
    pytest.main([__file__, "-v", "--tb=short", "-s"])