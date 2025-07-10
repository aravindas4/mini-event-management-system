"""
Timezone utility functions for handling timezone conversions
"""
import pytz
from datetime import datetime
from typing import Optional


def convert_utc_to_timezone(utc_datetime: datetime, timezone_str: str) -> datetime:
    """
    Convert UTC datetime to specified timezone
    
    Args:
        utc_datetime: UTC datetime object
        timezone_str: Target timezone string (e.g., 'Asia/Kolkata')
    
    Returns:
        Datetime converted to target timezone
    """
    if utc_datetime is None:
        return None
    
    # Ensure the datetime is timezone-aware and in UTC
    if utc_datetime.tzinfo is None:
        utc_datetime = pytz.UTC.localize(utc_datetime)
    elif utc_datetime.tzinfo != pytz.UTC:
        utc_datetime = utc_datetime.astimezone(pytz.UTC)
    
    # Convert to target timezone
    target_tz = pytz.timezone(timezone_str)
    return utc_datetime.astimezone(target_tz)


def validate_timezone(timezone_str: str) -> bool:
    """
    Validate if timezone string is valid
    
    Args:
        timezone_str: Timezone string to validate
    
    Returns:
        True if valid, False otherwise
    """
    try:
        pytz.timezone(timezone_str)
        return True
    except pytz.UnknownTimeZoneError:
        return False


def get_default_timezone() -> str:
    """
    Get default timezone for the application
    
    Returns:
        Default timezone string
    """
    return "Asia/Kolkata"


def get_available_timezones() -> list:
    """
    Get list of commonly used timezones
    
    Returns:
        List of timezone strings
    """
    return [
        "Asia/Kolkata",
        "UTC",
        "US/Eastern",
        "US/Central",
        "US/Mountain",
        "US/Pacific",
        "Europe/London",
        "Europe/Paris",
        "Europe/Berlin",
        "Asia/Tokyo",
        "Asia/Shanghai",
        "Asia/Dubai",
        "Australia/Sydney",
        "Australia/Melbourne"
    ]


def ensure_timezone_aware(dt: datetime, default_tz: Optional[str] = None) -> datetime:
    """
    Ensure datetime is timezone-aware
    
    Args:
        dt: Datetime object
        default_tz: Default timezone if datetime is naive (defaults to UTC)
    
    Returns:
        Timezone-aware datetime
    """
    if dt.tzinfo is None:
        tz = pytz.timezone(default_tz) if default_tz else pytz.UTC
        return tz.localize(dt)
    return dt


def validate_datetime_range(start_time: datetime, end_time: datetime, max_days: int = 7) -> None:
    """
    Validate datetime range with common business rules
    
    Args:
        start_time: Start datetime
        end_time: End datetime
        max_days: Maximum duration in days
    
    Raises:
        ValueError: If validation fails
    """
    # Ensure both datetimes are timezone-aware
    start_utc = ensure_timezone_aware(start_time)
    end_utc = ensure_timezone_aware(end_time)
    
    # Convert to UTC for comparison
    if start_utc.tzinfo != pytz.UTC:
        start_utc = start_utc.astimezone(pytz.UTC)
    if end_utc.tzinfo != pytz.UTC:
        end_utc = end_utc.astimezone(pytz.UTC)
    
    # Validate end time is after start time
    if end_utc <= start_utc:
        raise ValueError('End time must be after start time')
    
    # Validate duration
    duration = end_utc - start_utc
    if duration.days > max_days:
        raise ValueError(f'Duration cannot exceed {max_days} days')


def validate_future_datetime(dt: datetime) -> None:
    """
    Validate that datetime is in the future
    
    Args:
        dt: Datetime to validate
    
    Raises:
        ValueError: If datetime is not in the future
    """
    now_utc = datetime.now(pytz.UTC)
    dt_utc = ensure_timezone_aware(dt)
    
    if dt_utc.tzinfo != pytz.UTC:
        dt_utc = dt_utc.astimezone(pytz.UTC)
    
    if dt_utc <= now_utc:
        raise ValueError('Datetime must be in the future')