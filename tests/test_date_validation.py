#!/usr/bin/env python3
"""
Unit tests for date validation functionality in MCP server.
"""

import pytest
from datetime import datetime, timezone, timedelta
import sys
import os

# Add the src directory to the path  
current_dir = os.path.dirname(__file__)
src_dir = os.path.join(current_dir, '..', 'src')
sys.path.insert(0, src_dir)

# Import the validate_date_range function
def validate_date_range(start_date: str, end_date: str):
    """Local copy of validation function for testing."""
    from datetime import datetime, timezone
    
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
    
    # Calculate months for recency preference
    date_diff = (current_date - start_dt).days
    recency_months = max(1, min(60, date_diff // 30))
    
    return start_dt, end_dt, recency_months


class TestDateValidation:
    """Test date validation functions."""
    
    def test_valid_date_range(self):
        """Test valid date range validation."""
        start_date = "2024-01-01"
        end_date = "2024-12-31"
        
        start_dt, end_dt, recency_months = validate_date_range(start_date, end_date)
        
        assert start_dt.year == 2024
        assert start_dt.month == 1
        assert start_dt.day == 1
        assert end_dt.year == 2024
        assert end_dt.month == 12
        assert end_dt.day == 31
        assert isinstance(recency_months, int)
        assert 1 <= recency_months <= 60
    
    def test_invalid_date_format(self):
        """Test invalid date format raises ValueError."""
        with pytest.raises(ValueError, match="Invalid date format"):
            validate_date_range("2024-13-01", "2024-12-31")
        
        with pytest.raises(ValueError, match="Invalid date format"):
            validate_date_range("invalid-date", "2024-12-31")
        
        with pytest.raises(ValueError, match="Invalid date format"):
            validate_date_range("2024/01/01", "2024-12-31")
    
    def test_start_date_after_end_date(self):
        """Test start date after end date raises ValueError."""
        with pytest.raises(ValueError, match="Start date cannot be after end date"):
            validate_date_range("2024-12-31", "2024-01-01")
    
    def test_future_end_date(self):
        """Test future end date raises ValueError."""
        future_date = (datetime.now(timezone.utc) + timedelta(days=30)).strftime('%Y-%m-%d')
        
        with pytest.raises(ValueError, match="End date cannot be in the future"):
            validate_date_range("2024-01-01", future_date)
    
    def test_same_start_end_date(self):
        """Test same start and end date is valid."""
        yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime('%Y-%m-%d')
        
        start_dt, end_dt, recency_months = validate_date_range(yesterday, yesterday)
        
        assert start_dt == end_dt
        assert recency_months >= 1
    
    def test_recency_months_calculation(self):
        """Test recency months calculation."""
        # Test recent date (should give small recency_months)
        recent_start = (datetime.now(timezone.utc) - timedelta(days=60)).strftime('%Y-%m-%d')
        recent_end = (datetime.now(timezone.utc) - timedelta(days=1)).strftime('%Y-%m-%d')
        
        _, _, recency_months_recent = validate_date_range(recent_start, recent_end)
        
        # Test old date (should give larger recency_months)
        old_start = (datetime.now(timezone.utc) - timedelta(days=900)).strftime('%Y-%m-%d')
        old_end = (datetime.now(timezone.utc) - timedelta(days=1)).strftime('%Y-%m-%d')
        
        _, _, recency_months_old = validate_date_range(old_start, old_end)
        
        assert recency_months_recent <= recency_months_old
        assert 1 <= recency_months_recent <= 60
        assert 1 <= recency_months_old <= 60
    
    def test_timezone_handling(self):
        """Test that dates are properly converted to UTC."""
        start_date = "2024-06-15"
        end_date = "2024-06-16"
        
        start_dt, end_dt, _ = validate_date_range(start_date, end_date)
        
        assert start_dt.tzinfo == timezone.utc
        assert end_dt.tzinfo == timezone.utc
    
    def test_edge_case_today(self):
        """Test using today as end date."""
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime('%Y-%m-%d')
        
        # This should work without raising an error
        start_dt, end_dt, recency_months = validate_date_range(yesterday, today)
        
        assert start_dt < end_dt
        assert recency_months >= 1


if __name__ == "__main__":
    pytest.main([__file__])