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
import assistant
import actions
from globals import memory_storage  # Importing the global variable


# Import the Flask library to create a web server.
app = Flask(__name__)

# logging.basicConfig(level=logging.DEBUG)

# NOTE: Global variable to store the message history.
# For future development the store is where you would connect to the message history database.


def configure_slack_client():
    """Function to configure the Slack client to communicate with the user."""
    slack_token = os.getenv("SLACK_BOT_TOKEN")
    app_token = os.getenv("SLACK_APP_TOKEN")
    channel_id = os.getenv("SLACK_CHANNEL_ID")
    # Debugging line to print the token
    logging.debug(f"Slack Token: {slack_token}")
    # Debugging line to print the channel ID
    logging.debug(f"Channel ID: {channel_id}")
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
    # Initialize SocketModeClient with the app-level token.
    client = SocketModeClient(
        app_token=app_token, web_client=WebClient(token=slack_token)
    )

    # Initialize latest_timestamp with the current time.
    latest_timestamp = time.time()

    # Set to track processed event IDs.
    processed_event_ids = set()


    def handle_events(client: SocketModeClient, request: SocketModeRequest):
        """Function to handle the incoming events from the Slack API and invoke the correct outgoing responses."""
        nonlocal latest_timestamp

        # Initialize the WebClient to obtain the id of the bot.
        web_client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))

        # Get the bot user ID to ignore messages from the bot itself
        bot_user_id = web_client.auth_test()["user_id"]

        if request.type == "events_api":
            event = request.payload["event"]

            # Extract the event timestamp
            event_ts = event.get("event_ts")
            print(f"Received event: {event}")

            # Check if the event has already been processed
            if event_ts in processed_event_ids:
                logging.debug(f"Event {event_ts} already processed.")
                return

            # Check if the event is new
            if float(event_ts) <= latest_timestamp:
                logging.debug(f"Event {event_ts} is older than the latest timestamp.")
                return

            # Mark the event as processed
            processed_event_ids.add(event_ts)
            latest_timestamp = float(event_ts)

            # Handle different types of events
            # NOTE: The following code get's triggered when the bot is mentioned in a channel.
            if event.get("type") == "app_mention" and event.get("user") != bot_user_id:
                user = event.get("user")
                channel = event.get("channel")
                text = f"Hello <@{user}>! How can I help you today? :)"
                try:
                    client.web_client.chat_postMessage(channel=channel, text=text)
                except SlackApiError as e:
                    logging.error(f"Error sending message: {e.response['error']}")
            # NOTE: The following code get's triggered when a message is sent in a channel.
            elif (
                event.get("type") == "message"
                and "subtype" not in event
                and event.get("user") != bot_user_id
            ):
                user = event.get("user")
                channel = event.get("channel")
                text = event.get("text")
                handle_message(user, text, channel)
            # NOTE: The following code get's triggered when a reaction is added to a message.
            elif (
                event.get("type") == "reaction_added"
                and event.get("user") != bot_user_id
            ):
                user = event.get("user")
                reaction = event.get("reaction")
                item = event.get("item")
                channel = item.get("channel")
                logging.debug(
                    f"Handling reaction added by user {user}: {reaction} to item {item}"
                )
                handle_reaction_added(user, reaction, item, channel)
            # NOTE: The following code get's triggered when a reaction is removed from a message.
            elif (
                event.get("type") == "reaction_removed"
                and event.get("user") != bot_user_id
            ):
                user = event.get("user")
                reaction = event.get("reaction")
                item = event.get("item")
                channel = item.get("channel")
                logging.debug(
                    f"Handling reaction removed by user {user}: {reaction} from item {item}"
                )
                handle_reaction_removed(user, reaction, item, channel)

    # Add the event listener to the client.
    # if handle_events not in client.socket_mode_request_listeners:
    client.socket_mode_request_listeners.append(handle_events)

    # Establish a connection to the Slack API.
    print("Connecting to Slack API...")
    client.connect()
    print("Connected to Slack API.")

    # Start the Socket Mode client to process the events.
    while True:
        time.sleep(1)


def handle_message(user, question, channel):
    """Function to handle incoming messages to the bot."""
    # Obtain the slack token from the environment variables.
    slack_token = os.getenv("SLACK_BOT_TOKEN")

    # Setup and obtain the classification and conversational models.
    classification_model = assistant.initialize_classification_model(
        "src/prompt-templates/classifier-prompt.txt"
    )

    # Start the diagnostic experiments' timing and initialize the analytics .
    start_time = time.time()

    # Query the classifier to obtain the classifier values.
    # Variables description:
    # classifications is a dictionary containing the classification values.
    # classifier_tokens is the total number of tokens generated in the classifier model.
    classifications, classifier_tokens = assistant.query_classifier(
        classification_model, question
    )

    # Save the classification values inside of the classifications.json file in data.
    assistant.save_classification_to_json(classifications, question)

    # TODO: Implement the code to handle the user's question and take the desired action.
    action = actions.action_factory(classifications, question)
    action_prompt = action.execute()

    # print("action_result type:", type(action_result))
    print("action_result: ", action_prompt)

    # Setup and obtain the conversational model.
    conversational_model = assistant.initialize_conversational_model(action_prompt)

    # Ask the AI assistant to answer the question.
    response, conversation_tokens = assistant.query_ai_assistant(
        conversational_model, question
    )

    # End the diagnostic experiments' timing.
    end_time = time.time()

    # Calculate and output the model performance data to the terminal.
    assistant.calculate_model_diagnostics(
        start_time, end_time, classifier_tokens + conversation_tokens
    )

    # Calculate the total tokens from the classifier and conversational model.
    send_slack_message(slack_token, channel, response)


def handle_app_mention(user, question, channel):
    """Function to handle app mentions."""
    # Obtain the slack token from the environment variables.
    slack_token = os.getenv("SLACK_BOT_TOKEN")

    # Setup and obtain the classification and conversational models.
    classification_model = assistant.initialize_classification_model()

    # Start the diagnostic experiments' timing and initialize the analytics .
    start_time = time.time()

    # Query the classifier to obtain the classifier values.
    classifications, classifier_tokens = assistant.query_classifier(
        classification_model, question
    )

    # Save the classification values inside of the classifications.json file in data.
    assistant.save_classification_to_json(classifications, question)

    # Setup and obtain the conversational model.
    conversational_model = assistant.initialize_conversational_model(classifications)

    # Ask the AI assistant to answer the question.
    response, conversation_tokens = assistant.query_ai_assistant(
        classification_model, conversational_model, question
    )

    # End the diagnostic experiments' timing.
    end_time = time.time()

    # Calculate and output the model performance data to the terminal.
    assistant.calculate_model_diagnostics(
        start_time, end_time, classifier_tokens + conversation_tokens
    )

    # Calculate the total tokens from the classifier and conversational model.
    send_slack_message(slack_token, channel, response)


def handle_reaction_added(user, reaction, item, channel):
    """Function to handle reactions added to messages."""
    slack_token = os.getenv("SLACK_BOT_TOKEN")
    logging.info(f"User {user} added reaction {reaction} to item {item}")
    response_text = f"Hello <@{user}>, you added a reaction: {reaction}"

    # Send a message back to the channel.
    send_slack_message(slack_token, channel, response_text)


def handle_reaction_removed(user, reaction, item, channel):
    """Function to handle reactions removed from messages."""
    slack_token = os.getenv("SLACK_BOT_TOKEN")
    logging.info(f"User {user} removed reaction {reaction} from item {item}")
    response_text = f"Hello <@{user}>, you removed a reaction: {reaction}"

    # Send a message back to the channel.
    send_slack_message(slack_token, channel, response_text)
