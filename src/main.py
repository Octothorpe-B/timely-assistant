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


def main():
    """Main function to run the Timely program."""
    # Connect to the Slack API to send the user chats and notifications.
    slack_token, app_token, channel_id = slack_api.configure_slack_client()

    output = slack_api.list_channels(slack_token)

    # Run the flask app to listen for events from the Slack API.
    slack_api.process_event(slack_token, app_token, channel_id)


if __name__ == "__main__":
    # Obtain the current day's calendar events through the Google Cloud API.
    # Calendar Events Map: [0] = Event Name, [1] = Event Start Time, [2] = Event End Time, [3] = Event Location
    # calendar_events = google_calendar.obtain_calendar()

    # Save the obtained calendar events to a json file for later use.
    # google_calendar.save_calendar_events(calendar_events)
    main()
