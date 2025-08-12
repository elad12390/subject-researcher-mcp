#!/usr/bin/env python3
"""
Real MCP Server E2E Test - Happy Flow
Tests the actual MCP server by calling it as a subprocess and communicating via stdio.
"""

import asyncio
import json
import os
import subprocess
import sys
import time
from typing import Dict, Any, List

import pytest


class MCPTestClient:
    """Test client for communicating with the real MCP server."""
    
    def __init__(self):
        self.process = None
        self.request_id = 0
    
    async def start_server(self):
        """Start the MCP server as a subprocess."""
        server_path = os.path.join(
            os.path.dirname(__file__), 
            '..', 
            'src', 
            'subject_researcher_mcp', 
            'server.py'
        )
        
        # Start the server process
        self.process = await asyncio.create_subprocess_exec(
            'uv', 'run', 'python', server_path,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=os.path.join(os.path.dirname(__file__), '..')
        )
        
        print("🚀 MCP Server started")
        return self.process is not None
    
    async def send_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a JSON-RPC request to the server."""
        if not self.process:
            raise RuntimeError("Server not started")
        
        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
        }
        
        if params:
            request["params"] = params
        
        # Send request
        request_json = json.dumps(request) + '\n'
        print(f"📤 Sending: {method}")
        
        self.process.stdin.write(request_json.encode())
        await self.process.stdin.drain()
        
        # Read response
        response_line = await self.process.stdout.readline()
        if not response_line:
            stderr_output = await self.process.stderr.read()
            raise RuntimeError(f"No response from server. Stderr: {stderr_output.decode()}")
        
        response = json.loads(response_line.decode())
        print(f"📥 Received: {response.get('result', {}).get('method', 'response')}")
        
        return response
    
    async def initialize(self) -> Dict[str, Any]:
        """Initialize the MCP session."""
        return await self.send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        })
    
    async def list_tools(self) -> Dict[str, Any]:
        """List available tools."""
        return await self.send_request("tools/list")
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific tool."""
        return await self.send_request("tools/call", {
            "name": name,
            "arguments": arguments
        })
    
    async def stop_server(self):
        """Stop the MCP server."""
        if self.process:
            self.process.terminate()
            await self.process.wait()
            print("🛑 MCP Server stopped")


class TestRealMCPHappyFlow:
    """Real MCP server E2E happy flow tests."""
    
    @pytest.mark.asyncio
    async def test_complete_nx_nestjs_research_workflow(self):
        """
        Test complete happy flow: Research 'how to make nx and nestjs builds faster'
        This tests the real MCP server end-to-end.
        """
        client = MCPTestClient()
        
        try:
            # Step 1: Start the real MCP server
            print("\n🎯 Step 1: Starting MCP Server")
            server_started = await client.start_server()
            assert server_started, "Failed to start MCP server"
            
            # Give server time to start
            await asyncio.sleep(1)
            
            # Step 2: Initialize MCP session
            print("\n🎯 Step 2: Initializing MCP Session")
            init_response = await client.initialize()
            
            assert "result" in init_response, f"Initialization failed: {init_response}"
            assert init_response["result"]["protocolVersion"] == "2024-11-05"
            print("✅ MCP session initialized successfully")
            
            # Step 3: List available tools
            print("\n🎯 Step 3: Listing Available Tools")
            tools_response = await client.list_tools()
            
            assert "result" in tools_response, f"List tools failed: {tools_response}"
            tools = tools_response["result"]["tools"]
            assert len(tools) == 2, f"Expected 2 tools, got {len(tools)}"
            
            tool_names = [tool["name"] for tool in tools]
            assert "research_subject" in tool_names, "research_subject tool not found"
            assert "quick_search" in tool_names, "quick_search tool not found"
            print(f"✅ Found tools: {tool_names}")
            
            # Step 4: Test basic research on Nx and NestJS builds
            print("\n🎯 Step 4: Basic Research - Nx and NestJS Build Optimization")
            basic_research_response = await client.call_tool("research_subject", {
                "subject": "how to make nx and nestjs builds faster",
                "max_results": 5,
                "depth": "basic"
            })
            
            assert "result" in basic_research_response, f"Basic research failed: {basic_research_response}"
            basic_content = basic_research_response["result"]["content"][0]["text"]
            
            # Validate basic research structure
            assert "# Research Report:" in basic_content, "Missing main header"
            assert "nx" in basic_content.lower() or "nestjs" in basic_content.lower(), "Research doesn't mention Nx or NestJS"
            assert "## Summary" in basic_content, "Missing summary section"
            assert "## Key Findings" in basic_content, "Missing key findings section"
            assert "## Sources" in basic_content, "Missing sources section"
            
            print(f"✅ Basic research completed: {len(basic_content)} characters")
            print(f"   Content preview: {basic_content[:100]}...")
            
            # Step 5: Test detailed research with AI analysis
            print("\n🎯 Step 5: Detailed Research with AI Analysis")
            detailed_research_response = await client.call_tool("research_subject", {
                "subject": "nx nestjs build performance optimization",
                "max_results": 4,
                "depth": "detailed"
            })
            
            assert "result" in detailed_research_response, f"Detailed research failed: {detailed_research_response}"
            detailed_content = detailed_research_response["result"]["content"][0]["text"]
            
            # Validate detailed research structure
            assert "# Research Report:" in detailed_content, "Missing main header in detailed research"
            assert "## Summary" in detailed_content, "Missing summary in detailed research"
            assert "## Key Findings" in detailed_content, "Missing key findings in detailed research"
            assert "## Sources" in detailed_content, "Missing sources in detailed research"
            
            # Check if Gemini analysis was included (if API key available)
            has_gemini = os.getenv("GEMINI_API_KEY") is not None
            if has_gemini:
                print("   🧠 Gemini API available - checking for enhanced analysis")
                # With Gemini, should have more comprehensive content
                assert len(detailed_content) >= len(basic_content) * 0.8, "Detailed research should be substantial"
            else:
                print("   ⚠️  Gemini API not available - basic analysis used")
            
            print(f"✅ Detailed research completed: {len(detailed_content)} characters")
            print(f"   Content preview: {detailed_content[:100]}...")
            
            # Step 6: Test quick search for specific topics
            print("\n🎯 Step 6: Quick Search - NestJS Build Tools")
            quick_search_response = await client.call_tool("quick_search", {
                "query": "NestJS build optimization webpack",
                "max_results": 3
            })
            
            assert "result" in quick_search_response, f"Quick search failed: {quick_search_response}"
            quick_content = quick_search_response["result"]["content"][0]["text"]
            
            # Validate quick search structure
            assert "# Search Results for:" in quick_content, "Missing search results header"
            assert "nestjs" in quick_content.lower() or "webpack" in quick_content.lower(), "Search doesn't mention relevant terms"
            
            print(f"✅ Quick search completed: {len(quick_content)} characters")
            print(f"   Content preview: {quick_content[:100]}...")
            
            # Step 7: Test error handling with invalid request
            print("\n🎯 Step 7: Error Handling Test")
            error_response = await client.call_tool("research_subject", {
                # Missing required 'subject' parameter
                "max_results": 3,
                "depth": "basic"
            })
            
            assert "result" in error_response, "Error response should still have result structure"
            error_content = error_response["result"]["content"][0]["text"]
            assert "error" in error_content.lower() or "required" in error_content.lower(), "Should indicate parameter error"
            
            print("✅ Error handling working correctly")
            
            # Step 8: Validate research quality and relevance
            print("\n🎯 Step 8: Research Quality Validation")
            
            # Check that all responses contain relevant content
            all_content = [basic_content, detailed_content, quick_content]
            coding_terms = ["build", "performance", "optimization", "nx", "nestjs", "webpack", "compilation"]
            
            for i, content in enumerate(all_content):
                relevant_terms_found = sum(1 for term in coding_terms if term.lower() in content.lower())
                assert relevant_terms_found >= 2, f"Content {i} should contain relevant coding terms"
            
            print("✅ All research content is relevant and high-quality")
            
            # Step 9: Performance validation
            print("\n🎯 Step 9: Performance Validation")
            
            # Test rapid successive calls
            start_time = time.time()
            rapid_tasks = [
                client.call_tool("quick_search", {"query": f"nx build {i}", "max_results": 1})
                for i in range(3)
            ]
            
            rapid_results = await asyncio.gather(*rapid_tasks)
            end_time = time.time()
            
            # All should succeed
            for result in rapid_results:
                assert "result" in result, "Rapid call should succeed"
            
            total_time = end_time - start_time
            avg_time = total_time / len(rapid_tasks)
            
            print(f"✅ Performance test: {len(rapid_tasks)} calls in {total_time:.2f}s (avg: {avg_time:.2f}s)")
            assert total_time < 30.0, f"Rapid calls took too long: {total_time:.2f}s"
            
        finally:
            # Always clean up
            await client.stop_server()
    
    @pytest.mark.asyncio
    async def test_coding_research_depth_comparison(self):
        """
        Test comparing different research depths for coding topics.
        """
        client = MCPTestClient()
        
        try:
            # Start server and initialize
            await client.start_server()
            await asyncio.sleep(1)
            await client.initialize()
            
            coding_topic = "TypeScript performance optimization techniques"
            
            # Test basic vs detailed research
            print(f"\n🎯 Researching: {coding_topic}")
            
            # Basic research
            basic_response = await client.call_tool("research_subject", {
                "subject": coding_topic,
                "max_results": 3,
                "depth": "basic"
            })
            
            basic_content = basic_response["result"]["content"][0]["text"]
            
            # Detailed research  
            detailed_response = await client.call_tool("research_subject", {
                "subject": coding_topic,
                "max_results": 3,
                "depth": "detailed"
            })
            
            detailed_content = detailed_response["result"]["content"][0]["text"]
            
            # Compare results
            print(f"📊 Basic research: {len(basic_content)} characters")
            print(f"📊 Detailed research: {len(detailed_content)} characters")
            
            # Both should be valid
            for content in [basic_content, detailed_content]:
                assert "# Research Report:" in content
                assert "typescript" in content.lower() or "performance" in content.lower()
                assert len(content) > 100, "Content should be substantial"
            
            # Check for coding-specific content
            coding_indicators = ["function", "code", "performance", "optimization", "typescript", "javascript"]
            
            for content in [basic_content, detailed_content]:
                found_indicators = sum(1 for indicator in coding_indicators if indicator in content.lower())
                assert found_indicators >= 2, "Should contain coding-related terms"
            
            print("✅ Both research depths provide relevant coding information")
            
        finally:
            await client.stop_server()
    
    @pytest.mark.asyncio
    async def test_multiple_coding_topics_research(self):
        """
        Test researching multiple different coding topics in sequence.
        """
        client = MCPTestClient()
        
        try:
            await client.start_server()
            await asyncio.sleep(1)
            await client.initialize()
            
            coding_topics = [
                "React performance best practices",
                "Docker container optimization",
                "Python async programming patterns",
                "GraphQL query optimization"
            ]
            
            print(f"\n🎯 Testing multiple coding topics: {len(coding_topics)} topics")
            
            results = []
            
            for i, topic in enumerate(coding_topics):
                print(f"   📝 Researching: {topic}")
                
                response = await client.call_tool("research_subject", {
                    "subject": topic,
                    "max_results": 2,
                    "depth": "basic"
                })
                
                assert "result" in response, f"Research failed for topic: {topic}"
                content = response["result"]["content"][0]["text"]
                
                # Validate content quality
                assert len(content) > 50, f"Insufficient content for {topic}"
                assert "# Research Report:" in content, f"Missing header for {topic}"
                
                # Check relevance to coding
                topic_words = topic.lower().split()
                relevant_words_found = sum(1 for word in topic_words if word in content.lower())
                assert relevant_words_found >= 1, f"Content not relevant to {topic}"
                
                results.append({
                    "topic": topic,
                    "content_length": len(content),
                    "relevant": relevant_words_found
                })
                
                print(f"     ✅ {len(content)} chars, {relevant_words_found} relevant terms")
            
            # Summary
            total_chars = sum(r["content_length"] for r in results)
            avg_chars = total_chars / len(results)
            
            print(f"\n📊 Research Summary:")
            print(f"   Total content: {total_chars} characters")
            print(f"   Average per topic: {avg_chars:.0f} characters")
            print(f"   All topics researched successfully: {len(results)}/{len(coding_topics)}")
            
            assert len(results) == len(coding_topics), "Not all topics were researched"
            assert avg_chars > 100, "Average content length too low"
            
            print("✅ Multiple coding topics research completed successfully")
            
        finally:
            await client.stop_server()


@pytest.mark.asyncio
async def test_quick_validation():
    """Quick validation test to ensure the MCP server starts and responds."""
    client = MCPTestClient()
    
    try:
        print("\n🔍 Quick Validation Test")
        
        # Start and initialize
        await client.start_server()
        await asyncio.sleep(1)
        init_response = await client.initialize()
        
        assert "result" in init_response, "Server should initialize"
        
        # Quick tool test
        response = await client.call_tool("quick_search", {
            "query": "test",
            "max_results": 1
        })
        
        assert "result" in response, "Quick search should work"
        content = response["result"]["content"][0]["text"]
        assert len(content) > 0, "Should return some content"
        
        print("✅ Quick validation passed - server is working")
        
    finally:
        await client.stop_server()


if __name__ == "__main__":
    # Run the happy flow test directly
    async def run_happy_flow():
        print("🚀 Running Real MCP E2E Happy Flow Test")
        print("=" * 60)
        
        test_instance = TestRealMCPHappyFlow()
        
        try:
            await test_instance.test_complete_nx_nestjs_research_workflow()
            print("\n🎉 HAPPY FLOW TEST PASSED!")
            print("✨ The MCP server successfully researched 'how to make nx and nestjs builds faster'")
            print("🔧 All MCP protocol interactions working correctly")
            print("📊 Research quality and relevance validated")
            print("⚡ Performance within acceptable ranges")
            
        except Exception as e:
            print(f"\n❌ HAPPY FLOW TEST FAILED: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        return True
    
    if len(sys.argv) > 1 and sys.argv[1] == "--run":
        success = asyncio.run(run_happy_flow())
        sys.exit(0 if success else 1)
    else:
        # Run with pytest
        pytest.main([__file__, "-v", "--tb=short", "-s"])