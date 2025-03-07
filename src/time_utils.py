"""File to handle the getting of important time data."""

from datetime import datetime, timedelta
import pytz


def localize_dt(dt: datetime, tz: pytz.timezone):
    """Return a datetime in the given timezone. Localize if dt is naive; otherwise convert it."""
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        return tz.localize(dt)
    return dt.astimezone(tz)


def start_of_minute(dt: datetime, tz: pytz.timezone):
    """Calculate the start of the current minute."""
    dt = dt.replace(second=0, microsecond=0)
    return localize_dt(dt, tz)


def end_of_minute(dt: datetime, tz: pytz.timezone):
    """Calculate the end of the current minute."""
    dt = dt.replace(second=59, microsecond=999999)
    return localize_dt(dt, tz)


def start_of_hour(dt: datetime, tz: pytz.timezone):
    """Calculate the start of the current hour."""
    dt = dt.replace(minute=0, second=0, microsecond=0)
    return localize_dt(dt, tz)


def end_of_hour(dt: datetime, tz: pytz.timezone):
    """Calculate the end of the current hour."""
    dt = dt.replace(minute=59, second=59, microsecond=999999)
    return localize_dt(dt, tz)


def start_of_day(dt: datetime, tz: pytz.timezone):
    """Calculate the start of the current day."""
    dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)
    return localize_dt(dt, tz)


def end_of_day(dt: datetime, tz: pytz.timezone):
    """Calculate the end of the current day."""
    dt = dt.replace(hour=23, minute=59, second=59, microsecond=999999)
    return localize_dt(dt, tz)


def start_of_week(dt: datetime, tz: pytz.timezone):
    """Calculate the start of the current week (Monday)."""
    start = dt - timedelta(days=dt.weekday())
    start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    return localize_dt(start, tz)


def end_of_week(dt: datetime, tz: pytz.timezone):
    """Calculate the end of the current week (Sunday)."""
    start = dt - timedelta(days=dt.weekday())
    end = start + timedelta(days=6)
    end = end.replace(hour=23, minute=59, second=59, microsecond=999999)
    return localize_dt(end, tz)


def start_of_year(dt: datetime, tz: pytz.timezone):
    """Calculate the start of the current year."""
    dt = dt.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    return localize_dt(dt, tz)


def end_of_year(dt: datetime, tz: pytz.timezone):
    """Calculate the end of the current year."""
    dt = dt.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)
    return localize_dt(dt, tz)
