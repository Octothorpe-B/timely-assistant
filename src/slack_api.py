"""File to handle the Slack interactions between the AI assistant and the user."""


from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode.response import SocketModeResponse
from flask import Flask, request, jsonify
import os
import logging
import time

# Import the Flask library to create a web server.
app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)


def configure_slack_client():
    """Function to configure the Slack client to communicate with the user."""
    slack_token = os.getenv("SLACK_BOT_TOKEN")
    app_token = os.getenv("SLACK_APP_TOKEN")
    channel_id = os.getenv("SLACK_CHANNEL_ID")
    logging.debug(f"Slack Token: {slack_token}")  # Debugging line to print the token
    logging.debug(f"Channel ID: {channel_id}")  # Debugging line to print the channel ID
    return slack_token, app_token, channel_id


def send_slack_message(token, channel, text):
    client = WebClient(token=token)
    try:
        response = client.chat_postMessage(channel=channel, text=text)
        logging.debug(f"Message sent: {response['message']['text']}")
        return response
    except SlackApiError as e:
        logging.error(f"Error sending message: {e.response['error']}")


def list_channels(token):
    client = WebClient(token=token)
    try:
        response = client.conversations_list()
        for channel in response["channels"]:
            logging.info(f"Name: {channel['name']}, ID: {channel['id']}")
    except SlackApiError as e:
        logging.error(f"Error fetching conversations: {e.response['error']}")


def process_event(slack_token, app_token, channel_id):
    """Function to handle the bot event subscriptions sent by the Slack API."""
    # Initialize SocketModeClient with the app-level token
    client = SocketModeClient(
        app_token=app_token, web_client=WebClient(token=slack_token)
    )

    # Initialize latest_timestamp with the current time
    latest_timestamp = time.time()


    def handle_events(client: SocketModeClient, request: SocketModeRequest):
        """Function to handle the incoming events from the Slack API and invoke the correct outgoing responses."""
        nonlocal latest_timestamp
        if request.type == "events_api":
            event = request.payload["event"]
            print(f"Received event: {event}")
            
            # Activates when the user directly messages or mentions the bot.
            if event.get("type") == "app_mention":
                event_ts = float(event.get("ts"))
                if event_ts > latest_timestamp:
                    latest_timestamp = event_ts
                    user = event.get("user")
                    channel = event.get("channel")
                    text = f"Hello <@{user}>! How can I help you today? :)"
            # Activates if an indirect message is sent in Slack.
            elif event.get("type") == "message" and "subtype" not in event:
                event_ts = float(event.get("ts"))
                if event_ts > latest_timestamp:
                    latest_timestamp = event_ts

            # Activates if there's a reaction added.
            elif event.get("type") == "reaction_added":
                event_ts = float(event.get("ts"))
                if event_ts > latest_timestamp:
                    latest_timestamp = event_ts
                    user = event.get("user")
                    reaction = event.get("reaction")
                    item = event.get("item")
                    logging.debug(
                        f"Handling reaction added by user {user}: {reaction} to item {item}"
                    )
                    handle_reaction_added(user, reaction, item)

            # Activates if a reaction is removed.
            elif event.get("type") == "reaction_removed":
                event_ts = float(event.get("ts"))
                if event_ts > latest_timestamp:
                    latest_timestamp = event_ts
                    user = event.get("user")
                    reaction = event.get("reaction")
                    item = event.get("item")
                    logging.debug(
                        f"Handling reaction removed by user {user}: {reaction} from item {item}"
                    )
                    handle_reaction_removed(user, reaction, item)
                    # Send a message back to the channel
                    client.web_client.chat_postMessage(channel=channel, text=text)

    # Add the event listener to the client.
    client.socket_mode_request_listeners.append(handle_events)

    # Establish a connection to the Slack API.
    client.connect()

    # Start the Socket Mode client to process the events.
    while True:
        time.sleep(1)

    # Check if the event is a message from the user.


def handle_message(user, text, channel):
    """Function to handle incoming messages to the bot."""
    slack_token = os.getenv("SLACK_BOT_TOKEN")
    response_text = f"Hello <@{user}>, you said: {text}"
    logging.debug(
        f"Sending response to user {user} in channel {channel}: {response_text}"
    )
    send_slack_message(slack_token, channel, response_text)


def handle_app_mention(user, text, channel):
    """Function to handle app mentions."""
    slack_token = os.getenv("SLACK_BOT_TOKEN")
    response_text = f"Hello <@{user}>, you mentioned me: {text}"
    logging.debug(
        f"Sending response to user {user} in channel {channel}: {response_text}"
    )
    send_slack_message(slack_token, channel, response_text)


def handle_reaction_added(user, reaction, item):
    """Function to handle reactions added to messages."""
    logging.info(f"User {user} added reaction {reaction} to item {item}")


def handle_reaction_removed(user, reaction, item):
    """Function to handle reactions removed from messages."""
    logging.info(f"User {user} removed reaction {reaction} from item {item}")
