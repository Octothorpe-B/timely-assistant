"""
Main program file to manage the running of Timely.

Note: If you get this error: 

google.auth.exceptions.RefreshError: ('invalid_grant: Token has been expired or revoked ...)

Delete the token.json file in the src/data folder and re-run the program to authenticate your project.
"""

import slack_api
import google_calendar
import json
import time
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode.response import SocketModeResponse
from flask import Flask, request, jsonify
import os
import logging


def obtain_calendar():
    """Function to get the user's calendar to obtain their events and their locations."""
    # Initialize connection with Google Calendar API and return the service object that connects the program to the API.
    service = google_calendar.initialize_connection()

    # Initialize the connection with the Google Calendar API.
    calendar_events = google_calendar.get_next_24hr_events(service)

    # Output the calendar events for the next 24 hours to the terminal.
    print(calendar_events)

    return calendar_events


def save_calendar_events(calendar_events):
    """Function to save the calendar events to a json file."""
    with open("src/data/calendar.json", "w") as calendar:
        json.dump(calendar_events, calendar)


if __name__ == "__main__":
    # Obtain the current day's calendar events through the Google Cloud API.
    # Calendar Events Map: [0] = Event Name, [1] = Event Start Time, [2] = Event End Time, [3] = Event Location
    calendar_events = obtain_calendar()

    # Save the obtained calendar events to a json file for later use.
    save_calendar_events(calendar_events)

    # Connect to the Slack API to send the user chats and notifications.
    slack_token, app_token, channel_id = slack_api.configure_slack_client()

    print(f"Using Slack Token: {slack_token}")
    print(f"Using Channel ID: {channel_id}")

    output = slack_api.list_channels(slack_token)
    print(f"List Channels: {output}")

    # Run the flask app to listen for events from the Slack API.
    slack_api.process_event(slack_token, app_token, channel_id)

    # TODO: Implement code to convert the home address and destination address into latitude and longitude.

    # TODO: Implement code to calculate the travel time to the destination.

    # TODO: Implement logic to notify the user when to best start getting ready and when to leave.
