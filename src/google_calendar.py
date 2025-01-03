import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime
import json
import pytz

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def obtain_calendar():
    """Function to get the user's calendar to obtain their events and their locations."""
    # Initialize connection with Google Calendar API and return the service object that connects the program to the API.
    service = initialize_connection()

    # Initialize the connection with the Google Calendar API.
    calendar_events = get_next_24hr_events(service)

    # Return the calendar events.
    return calendar_events


def save_calendar_events(calendar_events):
    """Function to save the calendar events to a json file."""
    with open("src/data/calendar.json", "w") as calendar:
        json.dump(calendar_events, calendar)


def initialize_connection():
    """Initialize the programs connection with the Google Calendar API."""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.

    if os.path.exists("src/credentials/token.json"):
        creds = Credentials.from_authorized_user_file(
            "src/credentials/token.json", SCOPES
        )
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "src/credentials/credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("src/credentials/token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials = creds)

    except HttpError as error:
        print(f"An error occurred: {error}")

    return service


def get_time_zone_bounds(local_tz, lower_bound_time, upper_bound_time):
    """
    Obtain the time zone bounds for the current day.

    This function calculates the start and end of the current day in the specified time zone.
    It returns the start and end times in ISO 8601 format.

    Parameters:
    local_tz (pytz.timezone): The local time zone for which to calculate the bounds.
    lower_bound_time: the starting time boundary for the user's request.
    upper_bound_time: the ending time boundary for the user's request.

    Returns:
    tuple: A tuple containing the start and end of the day in ISO 8601 format.
    """

    # Get the current date and time in the specified time zone.
    now = datetime.now(local_tz)
    start_of_day_iso = local_tz.localize(
        datetime(now.year, now.month, now.day, 0, 0, 0)
    ).isoformat()
    end_of_day_iso = local_tz.localize(
        datetime(now.year, now.month, now.day, 23, 59, 59)
    ).isoformat()

    # Return the start and end of the day in ISO 8601 format.
    return start_of_day_iso, end_of_day_iso


def fetch_events(service, start_of_day_iso, end_of_day_iso):
    """ 
    Function to fetch the events for the current day from the Google Calendar API.
    """

    # Obtain the events for the current day.
    events_result = (service.events()
        .list(
            calendarId="primary",
            timeMin=start_of_day_iso,
            timeMax=end_of_day_iso,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )

    # Return the events for the current day.
    return events_result


def process_calendar_event(event, local_tz):
    """Process and format a single event."""
    # Get the start and end time of the calendar event.
    start_time, end_time = get_event_times(event)
    start_time_formatted, end_time_formatted = format_event_times(start_time, end_time, local_tz)
    summary = event.get("summary", "No Title")
    location = event.get("location", "No Location")

    # Determine if the event is an all-day event or a timed event.
    if is_all_day_event(start_time_formatted, end_time_formatted):
        event_type = "all-day"
    else:
        event_type = "timed"

    # Return the processed event data.
    return [event_type, summary, start_time_formatted, end_time_formatted, location]


def get_event_times(event):
    """Get the start and end times of an event."""
    start = event.get("start", {}).get("dateTime", event.get("start", {}).get("date", "No Start Time"))
    end = event.get("end", {}).get("dateTime", event.get("end", {}).get("date", "No End Time"))
    return start, end

def format_event_times(start, end, local_tz):
    """Format event times to 12-hour format with AM/PM."""
    # Parse the start and end times to datetime objects.
    try:
        start_time_dt = datetime.fromisoformat(start)
        end_time_dt = datetime.fromisoformat(end)
    except ValueError:
        print(f"Error parsing date: {start} or {end}")
        return "Invalid Time", "Invalid Time"
    
    # Format the start and end times to 12-hour format with AM/PM.
    start_time_formatted = start_time_dt.strftime("%I:%M %p")
    end_time_formatted = end_time_dt.strftime("%I:%M %p")

    # Return the formatted start and end times.
    return start_time_formatted, end_time_formatted


def is_all_day_event(start_time_formatted, end_time_formatted):
    """Check if an event is an all-day event."""
    if start_time_formatted == "12:00 AM" and end_time_formatted == "12:00 AM":
        return True
    else:
        return False


def get_next_24hr_events(service):
    """Function to obtain today's events stored in Google Calendar"""
    try:
        # Initialize an empty list for the calendar events.
        calendar_events = []

        # Define your local time zone
        local_tz = pytz.timezone("America/New_York")  # Replace with your local time zone

        # Obtain the current day events at the start of the day (0th hour) and the end of the day right before the 24th hour.
        start_of_day_iso, end_of_day_iso = get_time_zone_bounds(local_tz, 0, 1)
        events_result = fetch_events(service, start_of_day_iso, end_of_day_iso)

        # Obtain the events from the events_result dictionary.
        events = events_result.get("items", [])

        # If there are no events, return an empty list.
        if not events:
            return []

        for event in events:
            formatted_event = process_calendar_event(event, local_tz)
            calendar_events.append(formatted_event)
            print(formatted_event)

        return calendar_events
           
    except HttpError as error:
        print(f"An error occurred: {error}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []
