import os
import unittest
import sys
from unittest.mock import patch, Mock
from slack_sdk.errors import SlackApiError

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from slack_api import (
    configure_slack_client,
    send_slack_message,
    list_channels,
    process_event,
    handle_message,
    handle_app_mention,
    handle_reaction_added,
    handle_reaction_removed,
)


class TestSlackAPI(unittest.TestCase):
    @patch.dict(
        os.environ,
        {
            "SLACK_BOT_TOKEN": "xoxb-test-token",
            "SLACK_APP_TOKEN": "xapp-test-token",
            "SLACK_CHANNEL_ID": "C123456",
        },
    )
    def test_configure_slack_client(self):
        slack_token, app_token, channel_id = configure_slack_client()
        self.assertEqual(slack_token, "xoxb-test-token")
        self.assertEqual(app_token, "xapp-test-token")
        self.assertEqual(channel_id, "C123456")

    @patch("slack_api.WebClient")
    def test_send_slack_message(self, MockWebClient):
        mock_client = MockWebClient.return_value
        mock_client.chat_postMessage.return_value = {"message": {"text": "Hello"}}
        response = send_slack_message("xoxb-test-token", "C123456", "Hello")
        self.assertEqual(response["message"]["text"], "Hello")

    @patch("slack_api.WebClient")
    def test_send_slack_message_error(self, MockWebClient):
        mock_client = MockWebClient.return_value
        mock_client.chat_postMessage.side_effect = SlackApiError(
            "Error", {"error": "invalid_auth"}
        )
        with self.assertLogs(level="ERROR") as log:
            send_slack_message("xoxb-test-token", "C123456", "Hello")
            self.assertIn("Error sending message: invalid_auth", log.output[0])

    @patch("slack_api.WebClient")
    def test_list_channels(self, MockWebClient):
        mock_client = MockWebClient.return_value
        mock_client.conversations_list.return_value = {
            "channels": [{"name": "general", "id": "C123456"}]
        }
        with self.assertLogs(level="INFO") as log:
            list_channels("xoxb-test-token")
            self.assertIn("Name: general, ID: C123456", log.output[0])

    @patch("slack_api.WebClient")
    def test_list_channels_error(self, MockWebClient):
        mock_client = MockWebClient.return_value
        mock_client.conversations_list.side_effect = SlackApiError(
            "Error", {"error": "invalid_auth"}
        )
        with self.assertLogs(level="ERROR") as log:
            list_channels("xoxb-test-token")
            self.assertIn("Error fetching conversations: invalid_auth", log.output[0])

    #    @patch("slack_api.SocketModeClient.connect")
    #    @patch("slack_api.SocketModeClient")
    #    @patch("slack_api.WebClient")
    #    def test_process_event(self, MockWebClient, MockSocketModeClient, mock_connect):
    #        mock_client = MockSocketModeClient.return_value
    #        mock_web_client = MockWebClient.return_value
    #        mock_web_client.auth_test.return_value = {"user_id": "U123456"}
    #        process_event("xoxb-test-token", "xapp-test-token", "C123456")
    #        self.assertTrue(mock_connect.called)
    #        self.assertIn(
    #            mock_client.socket_mode_request_listeners[0],
    #            mock_client.socket_mode_request_listeners,
    #        )

    @patch("slack_api.assistant.initialize_classification_model")
    @patch("slack_api.assistant.query_classifier")
    @patch("slack_api.assistant.initialize_conversational_model")
    @patch("slack_api.assistant.query_ai_assistant")
    @patch("slack_api.assistant.calculate_model_diagnostics")
    @patch("slack_api.send_slack_message")
    def test_handle_message(
        self,
        mock_send_slack_message,
        mock_calculate_model_diagnostics,
        mock_query_ai_assistant,
        mock_initialize_conversational_model,
        mock_query_classifier,
        mock_initialize_classification_model,
    ):
        mock_initialize_classification_model.return_value = Mock()
        mock_query_classifier.return_value = (
            {"classification": "conversation", "sub-action": "answer"},
            10,
        )
        mock_initialize_conversational_model.return_value = Mock()
        mock_query_ai_assistant.return_value = ("response", 20)
        handle_message("U123456", "What is AI?", "C123456")
        self.assertTrue(mock_send_slack_message.called)

    @patch("slack_api.assistant.initialize_classification_model")
    @patch("slack_api.assistant.query_classifier")
    @patch("slack_api.assistant.initialize_conversational_model")
    @patch("slack_api.assistant.query_ai_assistant")
    @patch("slack_api.assistant.calculate_model_diagnostics")
    @patch("slack_api.send_slack_message")
    def test_handle_app_mention(
        self,
        mock_send_slack_message,
        mock_calculate_model_diagnostics,
        mock_query_ai_assistant,
        mock_initialize_conversational_model,
        mock_query_classifier,
        mock_initialize_classification_model,
    ):
        mock_initialize_classification_model.return_value = Mock()
        mock_query_classifier.return_value = ({"classification": "value"}, 10)
        mock_initialize_conversational_model.return_value = Mock()
        mock_query_ai_assistant.return_value = ("response", 20)
        handle_app_mention("U123456", "What is AI?", "C123456")
        self.assertTrue(mock_send_slack_message.called)

    @patch("slack_api.send_slack_message")
    def test_handle_reaction_added(self, mock_send_slack_message):
        handle_reaction_added("U123456", "thumbsup", {"channel": "C123456"}, "C123456")
        self.assertTrue(mock_send_slack_message.called)

    @patch("slack_api.send_slack_message")
    def test_handle_reaction_removed(self, mock_send_slack_message):
        handle_reaction_removed(
            "U123456", "thumbsup", {"channel": "C123456"}, "C123456"
        )
        self.assertTrue(mock_send_slack_message.called)


if __name__ == "__main__":
    unittest.main()
