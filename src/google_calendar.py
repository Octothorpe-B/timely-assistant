import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
import json
import pytz

import event_utils
import time_utils

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def obtain_calendar():
    """Function to get the user's calendar to obtain their events and their locations."""
    # Initialize connection with Google Calendar API and return the service object that connects the program to the API.
    service = initialize_connection()

    # Initialize the connection with the Google Calendar API.
    calendar_events = fetch_events(service)

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
        service = build("calendar", "v3", credentials=creds)

    except HttpError as error:
        print(f"An error occurred: {error}")

    return service


def route_calculate_time_bounds(classifications, local_tz):
    """Function to route the user's request to the corresponding function to correctly provide the requested date range for calendar events."""
    # Treat None and "null" as equivalent.
    specific_date = classifications[2]
    if specific_date is None or specific_date == "null":
        specific_date = "null"
    
    if classifications[1] != "null" and specific_date == "null":
        start_time_iso, end_time_iso = event_utils.calculate_relative_time_bounds(
            classifications, local_tz
        )
        return start_time_iso, end_time_iso
    elif classifications[1] != "null" and specific_date != "null":
        start_time_iso, end_time_iso = event_utils.calculate_relative_and_exact_time_bounds(
            classifications, local_tz
        )
        return start_time_iso, end_time_iso
    elif classifications[1] == "null" and specific_date != "null":
        start_time_iso, end_time_iso = event_utils.calculate_exact_range_time_bounds(
            classifications, local_tz
        )
        return start_time_iso, end_time_iso
    else:
        pass


def fetch_events(service, start_of_day_iso, end_of_day_iso):
    """
    Function to fetch the events for the current day from the Google Calendar API.
    """

    # Obtain the events for the current day.
    events_result = (
        service.events()
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
    try:
        # Get the start and end time of the calendar event.
        start_time, end_time = get_event_times(event)
        start_time_formatted, end_time_formatted = event_utils.format_event_times(
            start_time, end_time, local_tz
        )
        summary = event.get("summary", "No Title")
        location = event.get("location", "No Location")

        # Determine if the event is an all-day event or a timed event.
        if event_utils.is_all_day_event(start_time_formatted, end_time_formatted):
            event_type = "all-day"
        else:
            event_type = "timed"

        # Get the day of the event
        event_day = start_time.astimezone(local_tz).strftime("%A, %B %d, %Y")

        # Return the processed event data.
        return [
            event_type,
            summary,
            start_time_formatted,
            end_time_formatted,
            location,
            event_day,
        ]
    except Exception as e:
        print(f"An error occurred while running process_calendar_event(): {e}")
        return None


def get_event_times(event):
    """Get the start and end times of an event."""
    start = event.get("start", {}).get(
        "dateTime", event.get("start", {}).get("date", None)
    )
    end = event.get("end", {}).get("dateTime", event.get("end", {}).get("date", None))

    # Convert start and end times to datetime objects if they are strings
    if isinstance(start, str):
        try:
            start = datetime.fromisoformat(start)
        except ValueError:
            start = datetime.strptime(start, "%Y-%m-%d")
    if isinstance(end, str):
        try:
            end = datetime.fromisoformat(end)
        except ValueError:
            end = datetime.strptime(end, "%Y-%m-%d")

    return start, end


def get_time_bounded_events(service, classifications):
    """Function to obtain today's events stored in Google Calendar"""
    # try:
    # Initialize an empty list for the calendar events.
    calendar_events = []

    # Define your local time zone
    local_tz = pytz.timezone("America/New_York")  # Replace with your local time zone

    classifications = list(classifications.values())
    print("classifications!", classifications)

    # Ensure classifications are correctly handled
    classification1 = (
        classifications[0].lower()
        if classifications[0] and classifications[0].lower() != "none"
        else "null"
    )
    classification2 = (
        classifications[1].lower()
        if classifications[1] and classifications[1].lower() != "none"
        else "null"
    )
    classification3 = (
        classifications[2].lower()
        if classifications[2] and classifications[2].lower() != "none"
        else "null"
    )

    start_time_iso, end_time_iso = route_calculate_time_bounds(
        classifications, local_tz
    )

    print(f"Start Time: {start_time_iso}")
    print(f"End Time: {end_time_iso}")

    events_result = fetch_events(service, start_time_iso, end_time_iso)

    # Obtain the events from the events_result dictionary.
    events = events_result.get("items", [])

    # If there are no events, return an empty list.
    if not events:
        return []

    for event in events:
        formatted_event = process_calendar_event(event, local_tz)
        calendar_events.append(formatted_event)
        print(formatted_event)

    # Return the calendar events.
    if len(calendar_events) > 0:
        return calendar_events
    else:
        return "There are no calendar events within the specified timeframe."

    # except HttpError as error:
    #    print(f"An error occurred: {error}")
    #    return []
    # except Exception as e:
    #    print(f"An unexpected error occurred in get_time_bounded_events(): {e}")
    #    return []


if __name__ == "__main__":
    classifications = {
        "query-type": "recurring",
        "relative-time-direction": "0 Day, after",
        "specific-date": "null",
    }

    service = initialize_connection()

    calendar_events = get_time_bounded_events(service, classifications)

    print("\nCalendar Events:\n", calendar_events)
