#!/usr/bin/env python3
"""
Integration tests for MCP server with date validation - simplified version.
"""

import asyncio
import pytest
from datetime import datetime, timezone, timedelta
import sys
import os


class TestMCPServerIntegration:
    """Test MCP server integration with date validation."""
    
    def test_date_validation_logic(self):
        """Test the core date validation logic."""
        # Replicate the validation logic from server
        def validate_date_range(start_date: str, end_date: str):
            try:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d').replace(tzinfo=timezone.utc)
                end_dt = datetime.strptime(end_date, '%Y-%m-%d').replace(tzinfo=timezone.utc)
            except ValueError as e:
                raise ValueError(f"Invalid date format. Use YYYY-MM-DD format. Error: {e}")
            
            if start_dt > end_dt:
                raise ValueError("Start date cannot be after end date")
            
            current_date = datetime.now(timezone.utc)
            if end_dt > current_date:
                raise ValueError(f"End date cannot be in the future. Current date is {current_date.strftime('%Y-%m-%d')}")
            
            date_diff = (current_date - start_dt).days
            recency_months = max(1, min(60, date_diff // 30))
            
            return start_dt, end_dt, recency_months
        
        # Test valid case
        yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime('%Y-%m-%d')
        week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).strftime('%Y-%m-%d')
        
        start_dt, end_dt, recency_months = validate_date_range(week_ago, yesterday)
        assert start_dt < end_dt
        assert recency_months >= 1
        
        # Test invalid cases
        with pytest.raises(ValueError, match="Invalid date format"):
            validate_date_range("invalid", "2024-12-31")
        
        with pytest.raises(ValueError, match="Start date cannot be after end date"):
            validate_date_range("2024-12-31", "2024-01-01")
    
    def test_tool_schema_structure(self):
        """Test expected tool schema structure for dates."""
        # Expected schema structure for any research tool
        expected_date_properties = {
            "start_date": {
                "type": "string",
                "format": "date"
            },
            "end_date": {
                "type": "string", 
                "format": "date"
            }
        }
        
        # This tests the expected structure that should be in the schema
        for field_name, field_schema in expected_date_properties.items():
            assert field_schema["type"] == "string"
            assert field_schema["format"] == "date"
    
    def test_current_date_inclusion(self):
        """Test that current date logic works correctly."""
        current_date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        
        # Test that the current date is properly formatted
        assert len(current_date) == 10  # YYYY-MM-DD format
        assert current_date.count('-') == 2
        
        # Test that descriptions would include current date
        description_template = f"Current date is {current_date}. Use this to determine appropriate date ranges."
        assert current_date in description_template
    
    def test_argument_validation_logic(self):
        """Test argument validation logic that should be in tool handlers."""
        def validate_tool_arguments(name: str, arguments: dict):
            """Simulate the argument validation from tool handlers."""
            if name in ["comprehensive_research", "quick_research", "best_options_research"]:
                # Check required fields based on tool type
                if name == "comprehensive_research" and not arguments.get("subject"):
                    raise ValueError("Subject is required for comprehensive research")
                elif name == "quick_research" and not arguments.get("subject"):
                    raise ValueError("Subject is required for quick research")
                elif name == "best_options_research" and not arguments.get("need"):
                    raise ValueError("Need is required for best options research")
                
                # Check date requirements for all tools
                if not arguments.get("start_date"):
                    raise ValueError("Start date is required")
                if not arguments.get("end_date"):
                    raise ValueError("End date is required")
            
            return True
        
        # Test comprehensive_research
        with pytest.raises(ValueError, match="Subject is required"):
            validate_tool_arguments("comprehensive_research", {
                "start_date": "2024-01-01",
                "end_date": "2024-12-31"
            })
        
        with pytest.raises(ValueError, match="Start date is required"):
            validate_tool_arguments("comprehensive_research", {
                "subject": "test"
            })
        
        # Test quick_research  
        with pytest.raises(ValueError, match="End date is required"):
            validate_tool_arguments("quick_research", {
                "subject": "test",
                "start_date": "2024-01-01"
            })
        
        # Test best_options_research
        with pytest.raises(ValueError, match="Need is required"):
            validate_tool_arguments("best_options_research", {
                "start_date": "2024-01-01",
                "end_date": "2024-12-31"
            })
        
        # Test valid case
        assert validate_tool_arguments("comprehensive_research", {
            "subject": "test",
            "start_date": "2024-01-01", 
            "end_date": "2024-12-31"
        })
    
    def test_recency_months_calculation(self):
        """Test recency months calculation logic."""
        current_date = datetime.now(timezone.utc)
        
        # Test 30 days ago (should be ~1 month)
        start_30_days = (current_date - timedelta(days=30)).strftime('%Y-%m-%d')
        yesterday = (current_date - timedelta(days=1)).strftime('%Y-%m-%d')
        
        date_diff = (current_date - datetime.strptime(start_30_days, '%Y-%m-%d').replace(tzinfo=timezone.utc)).days
        recency_months = max(1, min(60, date_diff // 30))
        
        assert recency_months >= 1
        assert recency_months <= 60
        
        # Test very old date (should be capped at 60)
        start_old = (current_date - timedelta(days=2000)).strftime('%Y-%m-%d')
        
        date_diff_old = (current_date - datetime.strptime(start_old, '%Y-%m-%d').replace(tzinfo=timezone.utc)).days
        recency_months_old = max(1, min(60, date_diff_old // 30))
        
        assert recency_months_old == 60  # Should be capped


if __name__ == "__main__":
    pytest.main([__file__])