import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


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
        now = datetime.datetime.utcnow()
        start_of_day = (
            datetime.datetime(now.year, now.month, now.day, 0, 0, 0).isoformat() + "Z"
        )
        end_of_day = (
            datetime.datetime(now.year, now.month, now.day, 23, 59, 59).isoformat()
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
            summary = event.get("summary", "No Title")

            # Assess whether the event type is all day or timed and save the calendar data as needed.
            if "dateTime" in start:
                calendar_events.append(
                    ["all_day", event.get("summary", "No Title"), start, end]
                )
            else:
                calendar_events.append(["timed", event.get("summary", "No Title")])

            # If the last event is reached, return the function back to main.py
            if i == len(events) - 1:
                return calendar_events
