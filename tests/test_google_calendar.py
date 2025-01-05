import pytest
from unittest.mock import patch, Mock, mock_open
import google_calendar
import json
import pytz
from datetime import datetime, timedelta

# Mock data for testing
mock_event = {
    "start": {"dateTime": "2025-01-05T10:00:00-05:00"},
    "end": {"dateTime": "2025-01-05T11:00:00-05:00"},
    "summary": "Test Event",
    "location": "Test Location",
}

mock_events_result = {
    "items": [mock_event]
}

@patch('google_calendar.fetch_events')
@patch('google_calendar.initialize_connection')
def test_obtain_calendar(mock_initialize_connection, mock_fetch_events):
    mock_service = Mock()
    mock_initialize_connection.return_value = mock_service
    mock_fetch_events.return_value = mock_events_result

    events = google_calendar.obtain_calendar()
    assert len(events['items']) == 1
    assert events['items'][0]['summary'] == "Test Event"

@patch('google_calendar.json.dump')
@patch('builtins.open', new_callable=mock_open)
def test_save_calendar_events(mock_open, mock_json_dump):
    events = [{'summary': 'Test Event'}]
    google_calendar.save_calendar_events(events)
    mock_open.assert_called_once_with("src/data/calendar.json", "w")
    mock_json_dump.assert_called_once_with(events, mock_open())

@patch('google_calendar.Credentials')
@patch('google_calendar.build')
@patch('google_calendar.InstalledAppFlow')
@patch('google_calendar.os.path.exists')
@patch('google_calendar.open')
def test_initialize_connection(mock_open, mock_exists, mock_flow, mock_build, mock_credentials):
    mock_exists.return_value = False
    mock_flow.from_client_secrets_file().run_local_server.return_value = Mock()
    mock_build.return_value = Mock()

    service = google_calendar.initialize_connection()
    assert mock_build.called

@patch("google_calendar.fetch_events")
def test_get_time_bounded_events(mock_fetch_events):
    mock_fetch_events.return_value = mock_events_result
    service = Mock()
    local_tz = pytz.timezone("America/New_York")
    classifications = {"time": "1 Day", "time-direction": "after"}

    events = google_calendar.get_time_bounded_events(service, classifications)
    assert len(events) == 1
    assert events[0][1] == "Test Event"

def test_calculate_time_bounds():
    local_tz = pytz.timezone("America/New_York")
    start_time_iso, end_time_iso = google_calendar.calculate_time_bounds("1 Day", "after", local_tz)
    
    now = datetime.now(local_tz)
    expected_start_time = now.isoformat()
    expected_end_time = (now + timedelta(days=1)).isoformat()

    assert start_time_iso.startswith(expected_start_time[:19])
    assert end_time_iso.startswith(expected_end_time[:19])

def test_process_calendar_event():
    local_tz = pytz.timezone("America/New_York")
    event_data = google_calendar.process_calendar_event(mock_event, local_tz)
    
    assert event_data[1] == "Test Event"
    assert event_data[2] == "10:00 AM"
    assert event_data[3] == "11:00 AM"
    assert event_data[4] == "Test Location"

def test_get_event_times():
    start, end = google_calendar.get_event_times(mock_event)
    assert start.isoformat() == "2025-01-05T10:00:00-05:00"
    assert end.isoformat() == "2025-01-05T11:00:00-05:00"

def test_format_event_times():
    local_tz = pytz.timezone("America/New_York")
    start = datetime.fromisoformat("2025-01-05T10:00:00-05:00")
    end = datetime.fromisoformat("2025-01-05T11:00:00-05:00")
    start_time_formatted, end_time_formatted = google_calendar.format_event_times(start, end, local_tz)
    
    assert start_time_formatted == "10:00 AM"
    assert end_time_formatted == "11:00 AM"

def test_is_all_day_event():
    assert google_calendar.is_all_day_event("12:00 AM", "12:00 AM") == True
    assert google_calendar.is_all_day_event("10:00 AM", "11:00 AM") == False