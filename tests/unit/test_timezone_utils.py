"""
Unit tests for timezone utility functions
"""
import pytest
from datetime import datetime
import pytz

from app.core.utils.timezone_utils import (
    convert_utc_to_timezone,
    validate_timezone,
    get_default_timezone,
    get_available_timezones
)


class TestTimezoneUtils:
    """Test suite for timezone utility functions"""

    def test_validate_timezone_valid_timezones(self):
        """Test timezone validation with valid timezones"""
        valid_timezones = [
            "Asia/Kolkata",
            "UTC",
            "US/Eastern",
            "Europe/London",
            "Asia/Tokyo",
            "Australia/Sydney"
        ]
        
        for timezone in valid_timezones:
            assert validate_timezone(timezone) is True

    def test_validate_timezone_invalid_timezones(self):
        """Test timezone validation with invalid timezones"""
        invalid_timezones = [
            "Invalid/Timezone",
            "NonExistent/Zone",
            "Asia/InvalidCity",
            "US/InvalidState",
            "",
            "Not_A_Timezone"
        ]
        
        for timezone in invalid_timezones:
            assert validate_timezone(timezone) is False

    def test_get_default_timezone(self):
        """Test getting default timezone"""
        default_tz = get_default_timezone()
        assert default_tz == "Asia/Kolkata"
        assert validate_timezone(default_tz) is True

    def test_get_available_timezones(self):
        """Test getting available timezones list"""
        available_timezones = get_available_timezones()
        
        assert isinstance(available_timezones, list)
        assert len(available_timezones) > 0
        assert "Asia/Kolkata" in available_timezones
        assert "UTC" in available_timezones
        assert "US/Eastern" in available_timezones
        
        # All timezones should be valid
        for timezone in available_timezones:
            assert validate_timezone(timezone) is True

    def test_convert_utc_to_timezone_ist(self):
        """Test UTC to IST conversion"""
        # Arrange - 10:00 AM UTC on December 1, 2024
        utc_time = datetime(2024, 12, 1, 10, 0, 0, tzinfo=pytz.UTC)
        
        # Act
        ist_time = convert_utc_to_timezone(utc_time, "Asia/Kolkata")
        
        # Assert - IST is UTC+5:30, so 10:00 UTC = 15:30 IST
        assert ist_time.hour == 15
        assert ist_time.minute == 30
        assert ist_time.second == 0
        assert ist_time.tzinfo.zone == "Asia/Kolkata"

    def test_convert_utc_to_timezone_us_eastern(self):
        """Test UTC to US Eastern conversion"""
        # Arrange - 10:00 AM UTC on December 1, 2024 (EST, not DST)
        utc_time = datetime(2024, 12, 1, 10, 0, 0, tzinfo=pytz.UTC)
        
        # Act
        eastern_time = convert_utc_to_timezone(utc_time, "US/Eastern")
        
        # Assert - EST is UTC-5:00, so 10:00 UTC = 05:00 EST
        assert eastern_time.hour == 5
        assert eastern_time.minute == 0
        assert eastern_time.second == 0
        assert "Eastern" in str(eastern_time.tzinfo)

    def test_convert_utc_to_timezone_utc(self):
        """Test UTC to UTC conversion (should remain unchanged)"""
        # Arrange
        utc_time = datetime(2024, 12, 1, 10, 0, 0, tzinfo=pytz.UTC)
        
        # Act
        converted_time = convert_utc_to_timezone(utc_time, "UTC")
        
        # Assert
        assert converted_time == utc_time
        assert converted_time.tzinfo == pytz.UTC

    def test_convert_utc_to_timezone_none_input(self):
        """Test timezone conversion with None input"""
        # Act
        result = convert_utc_to_timezone(None, "Asia/Kolkata")
        
        # Assert
        assert result is None

    def test_convert_utc_to_timezone_naive_datetime(self):
        """Test timezone conversion with naive datetime (should be localized to UTC first)"""
        # Arrange - naive datetime
        naive_time = datetime(2024, 12, 1, 10, 0, 0)
        
        # Act
        ist_time = convert_utc_to_timezone(naive_time, "Asia/Kolkata")
        
        # Assert - should treat naive as UTC and convert to IST
        assert ist_time.hour == 15
        assert ist_time.minute == 30
        assert ist_time.tzinfo.zone == "Asia/Kolkata"

    def test_convert_utc_to_timezone_non_utc_input(self):
        """Test timezone conversion with non-UTC timezone input"""
        # Arrange - Create a time in IST
        ist_tz = pytz.timezone("Asia/Kolkata")
        ist_time = ist_tz.localize(datetime(2024, 12, 1, 15, 30, 0))
        
        # Act - Convert to US Eastern
        eastern_time = convert_utc_to_timezone(ist_time, "US/Eastern")
        
        # Assert - Should first convert to UTC, then to Eastern
        # 15:30 IST = 10:00 UTC = 05:00 EST
        assert eastern_time.hour == 5
        assert eastern_time.minute == 0

    def test_convert_utc_to_timezone_dst_transition(self):
        """Test timezone conversion during DST transition"""
        # Arrange - Summer time when DST is active
        utc_time = datetime(2024, 7, 1, 10, 0, 0, tzinfo=pytz.UTC)
        
        # Act
        eastern_time = convert_utc_to_timezone(utc_time, "US/Eastern")
        
        # Assert - EDT (Daylight Time) is UTC-4:00 in summer
        assert eastern_time.hour == 6
        assert eastern_time.minute == 0
        assert "EDT" in str(eastern_time.tzinfo) or "Eastern" in str(eastern_time.tzinfo)

    def test_convert_utc_to_timezone_multiple_conversions(self):
        """Test multiple timezone conversions with same base time"""
        # Arrange
        utc_time = datetime(2024, 12, 1, 12, 0, 0, tzinfo=pytz.UTC)  # Noon UTC
        
        # Act
        timezones_and_expected = [
            ("Asia/Kolkata", 17, 30),  # UTC+5:30
            ("Asia/Tokyo", 21, 0),     # UTC+9:00
            ("Europe/London", 12, 0),  # UTC+0:00 (GMT in winter)
            ("US/Pacific", 4, 0),      # UTC-8:00 (PST in winter)
        ]
        
        for timezone, expected_hour, expected_minute in timezones_and_expected:
            converted_time = convert_utc_to_timezone(utc_time, timezone)
            assert converted_time.hour == expected_hour
            assert converted_time.minute == expected_minute

    def test_convert_utc_to_timezone_edge_cases(self):
        """Test timezone conversion with edge cases"""
        # Test with midnight
        utc_midnight = datetime(2024, 12, 1, 0, 0, 0, tzinfo=pytz.UTC)
        ist_time = convert_utc_to_timezone(utc_midnight, "Asia/Kolkata")
        assert ist_time.hour == 5
        assert ist_time.minute == 30
        
        # Test with end of day
        utc_end_of_day = datetime(2024, 12, 1, 23, 59, 59, tzinfo=pytz.UTC)
        ist_time = convert_utc_to_timezone(utc_end_of_day, "Asia/Kolkata")
        assert ist_time.hour == 5
        assert ist_time.minute == 29
        assert ist_time.day == 2  # Should be next day

    def test_timezone_conversion_preserves_microseconds(self):
        """Test that timezone conversion preserves microseconds"""
        # Arrange
        utc_time = datetime(2024, 12, 1, 10, 30, 45, 123456, tzinfo=pytz.UTC)
        
        # Act
        ist_time = convert_utc_to_timezone(utc_time, "Asia/Kolkata")
        
        # Assert
        assert ist_time.microsecond == 123456
        assert ist_time.second == 45
        assert ist_time.minute == 0  # 30 + 30 = 60 -> 0 minutes + 1 hour
        assert ist_time.hour == 16   # 10 + 5 + 1 = 16