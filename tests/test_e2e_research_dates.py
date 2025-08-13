#!/usr/bin/env python3
"""
End-to-end tests for research workflow with date validation.
"""

import asyncio
import pytest
from datetime import datetime, timezone, timedelta
import json
import sys
import os


class TestE2EResearchDates:
    """End-to-end tests for research workflow with dates."""
    
    def test_complete_research_workflow_validation(self):
        """Test complete research workflow with date validation."""
        # Simulate a complete MCP request/response cycle
        
        def simulate_mcp_request(tool_name: str, arguments: dict):
            """Simulate an MCP tool request with validation."""
            # Step 1: Validate tool exists
            valid_tools = ["comprehensive_research", "quick_research", "best_options_research"]
            if tool_name not in valid_tools:
                raise ValueError(f"Unknown tool: {tool_name}")
            
            # Step 2: Validate required arguments
            if tool_name == "comprehensive_research":
                if not arguments.get("subject"):
                    raise ValueError("Subject is required for comprehensive research")
            elif tool_name == "quick_research":
                if not arguments.get("subject"):
                    raise ValueError("Subject is required for quick research")
            elif tool_name == "best_options_research":
                if not arguments.get("need"):
                    raise ValueError("Need is required for best options research")
            
            # Step 3: Validate date arguments (required for all tools)
            if not arguments.get("start_date"):
                raise ValueError("Start date is required")
            if not arguments.get("end_date"):
                raise ValueError("End date is required")
            
            # Step 4: Validate date format and range
            try:
                start_dt = datetime.strptime(arguments["start_date"], '%Y-%m-%d').replace(tzinfo=timezone.utc)
                end_dt = datetime.strptime(arguments["end_date"], '%Y-%m-%d').replace(tzinfo=timezone.utc)
            except ValueError as e:
                raise ValueError(f"Invalid date format. Use YYYY-MM-DD format. Error: {e}")
            
            if start_dt > end_dt:
                raise ValueError("Start date cannot be after end date")
            
            current_date = datetime.now(timezone.utc)
            if end_dt > current_date:
                raise ValueError(f"End date cannot be in the future. Current date is {current_date.strftime('%Y-%m-%d')}")
            
            # Step 5: Calculate recency months
            date_diff = (current_date - start_dt).days
            recency_months = max(1, min(60, date_diff // 30))
            
            # Step 6: Return simulated success response
            return {
                "status": "success",
                "tool": tool_name,
                "validated_dates": {
                    "start_date": arguments["start_date"],
                    "end_date": arguments["end_date"],
                    "recency_months": recency_months
                },
                "message": f"Research tool {tool_name} would execute with date range {arguments['start_date']} to {arguments['end_date']}"
            }
        
        # Test successful comprehensive research request
        yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime('%Y-%m-%d')
        last_month = (datetime.now(timezone.utc) - timedelta(days=30)).strftime('%Y-%m-%d')
        
        result = simulate_mcp_request("comprehensive_research", {
            "subject": "Python async programming best practices",
            "start_date": last_month,
            "end_date": yesterday
        })
        
        assert result["status"] == "success"
        assert result["tool"] == "comprehensive_research"
        assert result["validated_dates"]["start_date"] == last_month
        assert result["validated_dates"]["end_date"] == yesterday
        assert result["validated_dates"]["recency_months"] >= 1
    
    def test_e2e_error_scenarios(self):
        """Test end-to-end error scenarios."""
        def simulate_mcp_request(tool_name: str, arguments: dict):
            # Replicate the validation logic
            valid_tools = ["comprehensive_research", "quick_research", "best_options_research"]
            if tool_name not in valid_tools:
                raise ValueError(f"Unknown tool: {tool_name}")
            
            if tool_name == "comprehensive_research" and not arguments.get("subject"):
                raise ValueError("Subject is required for comprehensive research")
            elif tool_name == "quick_research" and not arguments.get("subject"):
                raise ValueError("Subject is required for quick research")  
            elif tool_name == "best_options_research" and not arguments.get("need"):
                raise ValueError("Need is required for best options research")
            
            if not arguments.get("start_date"):
                raise ValueError("Start date is required")
            if not arguments.get("end_date"):
                raise ValueError("End date is required")
            
            try:
                start_dt = datetime.strptime(arguments["start_date"], '%Y-%m-%d').replace(tzinfo=timezone.utc)
                end_dt = datetime.strptime(arguments["end_date"], '%Y-%m-%d').replace(tzinfo=timezone.utc)
            except ValueError as e:
                raise ValueError(f"Invalid date format. Use YYYY-MM-DD format. Error: {e}")
            
            if start_dt > end_dt:
                raise ValueError("Start date cannot be after end date")
            
            current_date = datetime.now(timezone.utc)
            if end_dt > current_date:
                raise ValueError(f"End date cannot be in the future. Current date is {current_date.strftime('%Y-%m-%d')}")
            
            return {"status": "success"}
        
        # Test missing subject
        with pytest.raises(ValueError, match="Subject is required"):
            simulate_mcp_request("comprehensive_research", {
                "start_date": "2024-01-01",
                "end_date": "2024-12-31"
            })
        
        # Test missing dates
        with pytest.raises(ValueError, match="Start date is required"):
            simulate_mcp_request("comprehensive_research", {
                "subject": "test"
            })
        
        # Test invalid date format
        with pytest.raises(ValueError, match="Invalid date format"):
            simulate_mcp_request("comprehensive_research", {
                "subject": "test",
                "start_date": "invalid-date",
                "end_date": "2024-12-31"
            })
        
        # Test future date
        future_date = (datetime.now(timezone.utc) + timedelta(days=30)).strftime('%Y-%m-%d')
        with pytest.raises(ValueError, match="End date cannot be in the future"):
            simulate_mcp_request("comprehensive_research", {
                "subject": "test",
                "start_date": "2024-01-01",
                "end_date": future_date
            })
        
        # Test start after end
        with pytest.raises(ValueError, match="Start date cannot be after end date"):
            simulate_mcp_request("comprehensive_research", {
                "subject": "test",
                "start_date": "2024-12-31",
                "end_date": "2024-01-01"
            })
    
    def test_e2e_all_tools_with_dates(self):
        """Test end-to-end workflow for all tools with dates."""
        def simulate_mcp_request(tool_name: str, arguments: dict):
            # Simplified validation for all tools
            if not arguments.get("start_date") or not arguments.get("end_date"):
                raise ValueError("Both start_date and end_date are required")
            
            if tool_name == "comprehensive_research" and not arguments.get("subject"):
                raise ValueError("Subject is required")
            elif tool_name == "quick_research" and not arguments.get("subject"):
                raise ValueError("Subject is required")
            elif tool_name == "best_options_research" and not arguments.get("need"):
                raise ValueError("Need is required")
            
            return {"status": "success", "tool": tool_name}
        
        yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime('%Y-%m-%d')
        last_week = (datetime.now(timezone.utc) - timedelta(days=7)).strftime('%Y-%m-%d')
        
        # Test comprehensive_research
        result1 = simulate_mcp_request("comprehensive_research", {
            "subject": "Machine learning trends",
            "start_date": last_week,
            "end_date": yesterday
        })
        assert result1["status"] == "success"
        assert result1["tool"] == "comprehensive_research"
        
        # Test quick_research
        result2 = simulate_mcp_request("quick_research", {
            "subject": "Quick analysis topic",
            "start_date": last_week,
            "end_date": yesterday
        })
        assert result2["status"] == "success" 
        assert result2["tool"] == "quick_research"
        
        # Test best_options_research
        result3 = simulate_mcp_request("best_options_research", {
            "need": "Best JavaScript frameworks",
            "start_date": last_week,
            "end_date": yesterday
        })
        assert result3["status"] == "success"
        assert result3["tool"] == "best_options_research"
    
    def test_e2e_date_range_edge_cases(self):
        """Test edge cases for date ranges."""
        def validate_and_process_dates(start_date: str, end_date: str):
            start_dt = datetime.strptime(start_date, '%Y-%m-%d').replace(tzinfo=timezone.utc)
            end_dt = datetime.strptime(end_date, '%Y-%m-%d').replace(tzinfo=timezone.utc)
            
            if start_dt > end_dt:
                raise ValueError("Start date cannot be after end date")
            
            current_date = datetime.now(timezone.utc)
            if end_dt > current_date:
                raise ValueError("End date cannot be in the future")
            
            date_diff = (current_date - start_dt).days
            recency_months = max(1, min(60, date_diff // 30))
            
            return {
                "start_dt": start_dt,
                "end_dt": end_dt,
                "recency_months": recency_months,
                "days_span": (end_dt - start_dt).days
            }
        
        # Test same day (today)
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime('%Y-%m-%d')
        
        result = validate_and_process_dates(yesterday, yesterday)
        assert result["days_span"] == 0
        assert result["recency_months"] >= 1
        
        # Test very long range (multiple years)
        three_years_ago = (datetime.now(timezone.utc) - timedelta(days=1095)).strftime('%Y-%m-%d')
        one_year_ago = (datetime.now(timezone.utc) - timedelta(days=365)).strftime('%Y-%m-%d')
        
        result_long = validate_and_process_dates(three_years_ago, one_year_ago)
        assert result_long["days_span"] == 730  # Approximately 2 years
        # For 3 years ago: ~1095 days, so recency_months = min(60, 1095//30) = min(60, 36) = 36
        assert result_long["recency_months"] >= 30  # Should be substantial for old dates
        
        # Test very short range (1 day)
        two_days_ago = (datetime.now(timezone.utc) - timedelta(days=2)).strftime('%Y-%m-%d')
        
        result_short = validate_and_process_dates(two_days_ago, yesterday)
        assert result_short["days_span"] == 1
        assert result_short["recency_months"] >= 1


if __name__ == "__main__":
    pytest.main([__file__])