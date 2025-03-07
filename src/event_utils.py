"""Function to handle the parsing, formatting, and getting of calendar events."""

from datetime import datetime, timedelta
import pytz
import time_utils


def format_event_times(start, end, local_tz):
    """Format event times to 12-hour format with AM/PM."""
    # Ensure start and end are datetime objects
    if isinstance(start, str):
        start = datetime.fromisoformat(start)
    if isinstance(end, str):
        end = datetime.fromisoformat(end)

    # Format the start and end times to 12-hour format with AM/PM.
    start_time_formatted = start.astimezone(local_tz).strftime("%I:%M %p")
    end_time_formatted = end.astimezone(local_tz).strftime("%I:%M %p")

    # Return the formatted start and end times.
    return start_time_formatted, end_time_formatted

def is_all_day_event(start_time_formatted, end_time_formatted):
    """Check if an event is an all-day event."""
    if start_time_formatted == "12:00 AM" and end_time_formatted == "12:00 AM":
        return True
    else:
        return False
    

def calculate_relative_time_bounds(classifications, local_tz):
    """Calculate the time bounding fields based on the provided time field and time direction field."""
    naive_now = datetime.now()
    now = local_tz.localize(naive_now)
    
    # Parse the classifier output: e.g., "1 Week, after" or "0 Year, same"
    time_str, relativity = str.split(classifications[1], ",")
    time_str = time_str.strip()      # e.g., "0 Year"
    relativity = relativity.strip().lower()  # e.g., "same"

    try:
        time_value, time_unit = time_str.split()
        time_value = int(time_value)
    except ValueError:
        time_value = 0
        time_unit = "day"
    
    # Define mapping for the 'same' case.
    same_mapping = {
        "minute": (time_utils.start_of_minute, time_utils.end_of_minute),
        "minutes": (time_utils.start_of_minute, time_utils.end_of_minute),
        "hour": (time_utils.start_of_hour, time_utils.end_of_hour),
        "hours": (time_utils.start_of_hour, time_utils.end_of_hour),
        "day": (time_utils.start_of_day, time_utils.end_of_day),
        "days": (time_utils.start_of_day, time_utils.end_of_day),
        "week": (time_utils.start_of_week, time_utils.end_of_week),
        "weeks": (time_utils.start_of_week, time_utils.end_of_week),
        "year": (time_utils.start_of_year, time_utils.end_of_year),
        "years": (time_utils.start_of_year, time_utils.end_of_year),
    }
    
    # Calculate boundaries based on the time direction.
    if relativity == "before":
        # Use time delta calculations.
        if time_unit.lower() in ["minute", "minutes"]:
            time_delta = timedelta(minutes=time_value)
        elif time_unit.lower() in ["hour", "hours"]:
            time_delta = timedelta(hours=time_value)
        elif time_unit.lower() in ["day", "days"]:
            time_delta = timedelta(days=time_value)
        elif time_unit.lower() in ["week", "weeks"]:
            time_delta = timedelta(weeks=time_value)
        elif time_unit.lower() in ["year", "years"]:
            time_delta = timedelta(days=365 * time_value)
        else:
            time_delta = timedelta(0)
        
        start_time = now - time_delta
        end_time = now
    elif relativity == "after":
        # Use time delta calculations.
        if time_unit.lower() in ["minute", "minutes"]:
            time_delta = timedelta(minutes=time_value)
        elif time_unit.lower() in ["hour", "hours"]:
            time_delta = timedelta(hours=time_value)
        elif time_unit.lower() in ["day", "days"]:
            time_delta = timedelta(days=time_value)
        elif time_unit.lower() in ["week", "weeks"]:
            time_delta = timedelta(weeks=time_value)
        elif time_unit.lower() in ["year", "years"]:
            time_delta = timedelta(days=365 * time_value)
        else:
            time_delta = timedelta(0)
        
        start_time = now
        end_time = now + time_delta
    elif relativity == "same":
        # Use mapping based on the provided time unit.
        func_pair = same_mapping.get(time_unit.lower())
        if func_pair:
            start_func, end_func = func_pair
            start_time = start_func(now, local_tz)
            end_time = end_func(now, local_tz)
        else:
            # Fall back to day boundaries if time_unit is unrecognized.
            start_time = time_utils.start_of_day(now, local_tz)
            end_time = time_utils.end_of_day(now, local_tz)
    elif relativity == "null":
        start_time = now
        end_time = now
    else:
        start_time = now
        end_time = now

    start_time_iso = start_time.isoformat()
    end_time_iso = end_time.isoformat()

    return start_time_iso, end_time_iso


def calculate_exact_range_time_bounds(classifications, local_tz):
    """Calculate the time bounding fields based on the provided time field and time direction field."""

    return 69, 69


def calculate_relative_and_exact_time_bounds(classifications, local_tz):
    """Calculate the time bounding fields based on the provided time field and time direction field."""

    return 96, 96