#!/usr/bin/env python3
"""
Integration tests for MCP server with date validation.
"""

import asyncio
import pytest
from datetime import datetime, timezone, timedelta
import sys
import os

# Add the src directory to the path
current_dir = os.path.dirname(__file__)
src_dir = os.path.join(current_dir, '..', 'src')
sys.path.insert(0, src_dir)


class TestMCPServerDates:
    """Test MCP server date functionality."""
    
    @pytest.fixture
    def mock_server_tools(self):
        """Mock the server tools list function."""
        from subject_researcher_mcp import server
        
        # Mock the list_tools function for testing
        async def mock_list_tools():
            return await server.handle_list_tools()
        
        return mock_list_tools
    
    @pytest.mark.asyncio
    async def test_tool_descriptions_include_current_date(self, mock_server_tools):
        """Test that tool descriptions include current date."""
        tools = await mock_server_tools()
        
        current_date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        
        for tool in tools:
            assert current_date in tool.description
            
            # Check that date fields are required
            assert "start_date" in tool.inputSchema["required"]
            assert "end_date" in tool.inputSchema["required"]
            
            # Check date field descriptions mention current date
            start_date_desc = tool.inputSchema["properties"]["start_date"]["description"]
            end_date_desc = tool.inputSchema["properties"]["end_date"]["description"]
            
            assert current_date in start_date_desc
            assert current_date in end_date_desc
    
    @pytest.mark.asyncio
    async def test_comprehensive_research_requires_dates(self):
        """Test comprehensive research tool requires date parameters."""
        from subject_researcher_mcp.server import handle_call_tool
        
        # Test missing start_date
        with pytest.raises(ValueError, match="Start date is required"):
            await handle_call_tool("comprehensive_research", {
                "subject": "test subject",
                "end_date": "2024-12-31"
            })
        
        # Test missing end_date
        with pytest.raises(ValueError, match="End date is required"):
            await handle_call_tool("comprehensive_research", {
                "subject": "test subject", 
                "start_date": "2024-01-01"
            })
        
        # Test missing subject
        with pytest.raises(ValueError, match="Subject is required"):
            await handle_call_tool("comprehensive_research", {
                "start_date": "2024-01-01",
                "end_date": "2024-12-31"
            })
    
    @pytest.mark.asyncio
    async def test_quick_research_requires_dates(self):
        """Test quick research tool requires date parameters."""
        from subject_researcher_mcp.server import handle_call_tool
        
        # Test missing dates
        with pytest.raises(ValueError, match="Start date is required"):
            await handle_call_tool("quick_research", {
                "subject": "test subject"
            })
    
    @pytest.mark.asyncio
    async def test_best_options_research_requires_dates(self):
        """Test best options research tool requires date parameters."""
        from subject_researcher_mcp.server import handle_call_tool
        
        # Test missing dates
        with pytest.raises(ValueError, match="Start date is required"):
            await handle_call_tool("best_options_research", {
                "need": "test need"
            })
    
    @pytest.mark.asyncio
    async def test_invalid_date_format_handling(self):
        """Test invalid date format handling."""
        from subject_researcher_mcp.server import handle_call_tool
        
        with pytest.raises(ValueError, match="Invalid date format"):
            await handle_call_tool("comprehensive_research", {
                "subject": "test subject",
                "start_date": "invalid-date",
                "end_date": "2024-12-31"
            })
    
    @pytest.mark.asyncio
    async def test_future_date_handling(self):
        """Test future date handling."""
        from subject_researcher_mcp.server import handle_call_tool
        
        future_date = (datetime.now(timezone.utc) + timedelta(days=30)).strftime('%Y-%m-%d')
        
        with pytest.raises(ValueError, match="End date cannot be in the future"):
            await handle_call_tool("comprehensive_research", {
                "subject": "test subject",
                "start_date": "2024-01-01",
                "end_date": future_date
            })
    
    @pytest.mark.asyncio 
    async def test_start_after_end_date_handling(self):
        """Test start date after end date handling."""
        from subject_researcher_mcp.server import handle_call_tool
        
        with pytest.raises(ValueError, match="Start date cannot be after end date"):
            await handle_call_tool("comprehensive_research", {
                "subject": "test subject",
                "start_date": "2024-12-31",
                "end_date": "2024-01-01"
            })
    
    def test_date_fields_schema_validation(self):
        """Test date fields have proper schema validation."""
        from subject_researcher_mcp.server import handle_list_tools
        
        tools = asyncio.run(handle_list_tools())
        
        for tool in tools:
            schema = tool.inputSchema
            
            # Check start_date field
            start_date_field = schema["properties"]["start_date"]
            assert start_date_field["type"] == "string"
            assert start_date_field["format"] == "date"
            
            # Check end_date field  
            end_date_field = schema["properties"]["end_date"]
            assert end_date_field["type"] == "string"
            assert end_date_field["format"] == "date"
    
    @pytest.mark.asyncio
    async def test_valid_date_range_processing(self):
        """Test that valid date ranges are processed correctly."""
        from subject_researcher_mcp.server import validate_date_range
        
        yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime('%Y-%m-%d')
        week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).strftime('%Y-%m-%d')
        
        start_dt, end_dt, recency_months = validate_date_range(week_ago, yesterday)
        
        assert start_dt < end_dt
        assert isinstance(recency_months, int)
        assert recency_months >= 1


if __name__ == "__main__":
    pytest.main([__file__])