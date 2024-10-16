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

    # TODO: Obtain the current date of when this program is running.

    # TODO: Calculate the end date of the current date.

    # TODO: Input the the lower and upper bound time into the timeMax and timeMin parameters of the list event api function.

    while True:
        events = (
            service.events().list(calendarId="primary", pageToken=page_token).execute()
        )
        for event in events["items"]:
            print(event["summary"])
        page_token = events.get("nextPageToken")
        if not page_token:
            break
