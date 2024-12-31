import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime
import json

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def obtain_calendar():
    """Function to get the user's calendar to obtain their events and their locations."""
    # Initialize connection with Google Calendar API and return the service object that connects the program to the API.
    service = initialize_connection()

    # Initialize the connection with the Google Calendar API.
    calendar_events = get_next_24hr_events(service)

    # Output the calendar events for the next 24 hours to the terminal.
    # print(calendar_events)

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


def get_next_24hr_events(service):
    """Function to obtain today's events stored in Google Calendar"""
    page_token = None
    calendar_events = []

    while True:
        # Obtain the current day events at the start of the day (0th hour) and the end of the day right before the 24th hour.
        now = datetime.utcnow()
        start_of_day = (
            datetime(now.year, now.month, now.day, 0, 0, 0).isoformat() + "Z"
        )
        end_of_day = (
            datetime(now.year, now.month, now.day, 23, 59, 59).isoformat()
            + "Z"
        )

        # Obtain the events for the current day.
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=start_of_day,
                timeMax=end_of_day,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        # Obtain the events from the events_result dictionary.
        events = events_result.get("items", [])

        # If there are no events, print a message to the user.
        if not events:
            print("No events found for today.")
            return

        for i, event in enumerate(events):
            # Get the start and end time of the calendar events.
            start = event.get("start", {})
            end = event.get("end", {})

            # Obtain the start and summary of the i-th calendar event.
            start = event.get("start", {}).get(
                "dateTime", event.get("start", {}).get("date", "No Start Time")
            )
            end = event.get("end", {}).get(
                "dateTime", event.get("end", {}).get("date", "No End Time")
            )

            # Convert the event times to 12-hour format with AM/PM.
            start_time_dt = datetime.fromisoformat(start)
            end_time_dt = datetime.fromisoformat(end)
            start_time_formatted = start_time_dt.strftime("%I:%M %p")
            end_time_formatted = end_time_dt.strftime("%I:%M %p")


            summary = event.get("summary", "No Title")
            location = event.get("location", "No Location")

            # Assess whether the event type is all day or timed and save the calendar data as needed.
            # This code segment triggers if the event is an all-day event.
            if "dateTime" in start:
                calendar_events.append(
                    ["all_day", event.get("summary", "No Title"), start, end, location]
                )
            # This code segment triggers if the event is a timed event.
            else:
                calendar_events.append(
                    ["timed", event.get("summary", "No Title"), start_time_formatted, end_time_formatted, location]
                )

            # If the last event is reached, return the function back to main.py
            if i == len(events) - 1:
                return calendar_events
