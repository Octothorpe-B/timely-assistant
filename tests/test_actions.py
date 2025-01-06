"""Test the action classes and factory function."""

import pytest
import os
import sys
from unittest.mock import patch, Mock, mock_open
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode import SocketModeClient

SocketModeClient.socket_mode_request_listeners = []
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from actions import (
    BaseAction,
    CalendarAction,
    ReminderAction,
    ConversationAction,
    OtherAction,
    action_factory,
)


class TestActions:
    """Test the action classes and factory function."""

    def test_base_action_execute(self):
        """Test the execute method of BaseAction."""
        action = BaseAction({}, "")
        with pytest.raises(NotImplementedError):
            action.execute()

    @patch("google_calendar.initialize_connection")
    @patch("assistant.initialize_classification_model")
    @patch("assistant.query_classifier")
    @patch("google_calendar.get_time_bounded_events")
    @patch("google_calendar.save_calendar_events")
    @patch("builtins.open", new_callable=mock_open, read_data="Prompt template content")
    def test_calendar_action_get_event_info(
        self,
        mock_open,
        mock_save_calendar_events,
        mock_get_time_bounded_events,
        mock_query_classifier,
        mock_initialize_classification_model,
        mock_initialize_connection,
    ):
        """Test the get_event_info method of CalendarAction."""
        mock_initialize_connection.return_value = "mock_service"
        mock_initialize_classification_model.return_value = "mock_classification_model"
        mock_query_classifier.return_value = ({"key": "value"}, 10)
        mock_get_time_bounded_events.return_value = [
            (
                "Meeting",
                "Team Sync",
                "10:00 AM",
                "11:00 AM",
                "Conference Room",
                "Monday",
            ),
        ]
        action = CalendarAction(
            {"sub-action": "get_event_info"}, "What meetings do I have today?"
        )
        result = action.get_event_info()
        expected_result = [
            "Event Type: Meeting | Event Title: Team Sync | Start Time: 10:00 AM | End Time: 11:00 AM | Location: Conference Room | Day of Event: Monday"
        ]

        # Load the calendar action prompt template.
        with open("src/prompt-templates/calendar-action-prompt.txt", "r") as file:
            prompt_template = file.read()

        # Format the calendar prompt with the calendar data.
        calendar_prompt = prompt_template.format(
            classifier_data=mock_initialize_classification_model.return_value,
            calendar_data=expected_result,
        )

        assert result == calendar_prompt

    def test_calendar_action_add_event(self):
        """Test the add_event method of CalendarAction."""
        action = CalendarAction({"sub-action": "add"}, "Add a meeting at 10 AM")
        with patch("builtins.print") as mock_print:
            action.add_event()
            mock_print.assert_called_once_with("Adding calendar event")

    def test_calendar_action_update_event(self):
        """Test the update_event method of CalendarAction."""
        action = CalendarAction({"sub-action": "update"}, "Update the meeting time")
        with patch("builtins.print") as mock_print:
            action.update_event()
            mock_print.assert_called_once_with("Updating calendar event")

    def test_calendar_action_delete_event(self):
        """Test the delete_event method of CalendarAction."""
        action = CalendarAction({"sub-action": "delete"}, "Delete the meeting")
        with patch("builtins.print") as mock_print:
            action.delete_event()
            mock_print.assert_called_once_with("Deleting calendar event")

    def test_calendar_action_execute(self):
        """Test the execute method of CalendarAction."""
        with patch.object(CalendarAction, "add_event") as mock_add_event:
            action = CalendarAction({"sub-action": "add"}, "Add a meeting at 10 AM")
            action.execute()
            mock_add_event.assert_called_once()

        with patch.object(CalendarAction, "update_event") as mock_update_event:
            action = CalendarAction({"sub-action": "update"}, "Update the meeting time")
            action.execute()
            mock_update_event.assert_called_once()

        with patch.object(CalendarAction, "delete_event") as mock_delete_event:
            action = CalendarAction({"sub-action": "delete"}, "Delete the meeting")
            action.execute()
            mock_delete_event.assert_called_once()

        with patch.object(CalendarAction, "get_event_info") as mock_get_event_info:
            action = CalendarAction(
                {"sub-action": "get-info"}, "What meetings do I have today?"
            )
            action.execute()
            mock_get_event_info.assert_called_once()

        with patch.object(CalendarAction, "respond") as mock_respond:
            action = CalendarAction({"sub-action": "null"}, "No specific action")
            action.execute()
            mock_respond.assert_called_once()

    def test_reminder_action_add_reminder(self):
        """Test the add_reminder method of ReminderAction."""
        action = ReminderAction({"sub-action": "add"}, "Add a reminder to call John")
        with patch("builtins.print") as mock_print:
            action.add_reminder()
            mock_print.assert_called_once_with("Adding reminder")

    def test_reminder_action_update_reminder(self):
        """Test the update_reminder method of ReminderAction."""
        action = ReminderAction({"sub-action": "update"}, "Update the reminder time")
        with patch("builtins.print") as mock_print:
            action.update_reminder()
            mock_print.assert_called_once_with("Updating reminder")

    def test_reminder_action_delete_reminder(self):
        """Test the delete_reminder method of ReminderAction."""
        action = ReminderAction({"sub-action": "delete"}, "Delete the reminder")
        with patch("builtins.print") as mock_print:
            action.delete_reminder()
            mock_print.assert_called_once_with("Deleting reminder")

    def test_reminder_action_get_reminder_info(self):
        """Test the get_reminder_info method of ReminderAction."""
        action = ReminderAction({"sub-action": "get-info"}, "What reminders do I have?")
        with patch("builtins.print") as mock_print:
            action.get_reminder_info()
            mock_print.assert_called_once_with("Getting reminder info")

    def test_reminder_action_execute(self):
        """Test the execute method of ReminderAction."""
        with patch.object(ReminderAction, "add_reminder") as mock_add_reminder:
            action = ReminderAction(
                {"sub-action": "add"}, "Add a reminder to call John"
            )
            action.execute()
            mock_add_reminder.assert_called_once()

        with patch.object(ReminderAction, "update_reminder") as mock_update_reminder:
            action = ReminderAction(
                {"sub-action": "update"}, "Update the reminder time"
            )
            action.execute()
            mock_update_reminder.assert_called_once()

        with patch.object(ReminderAction, "delete_reminder") as mock_delete_reminder:
            action = ReminderAction({"sub-action": "delete"}, "Delete the reminder")
            action.execute()
            mock_delete_reminder.assert_called_once()

        with patch.object(
            ReminderAction, "get_reminder_info"
        ) as mock_get_reminder_info:
            action = ReminderAction(
                {"sub-action": "get-info"}, "What reminders do I have?"
            )
            action.execute()
            mock_get_reminder_info.assert_called_once()

        with patch.object(ReminderAction, "respond") as mock_respond:
            action = ReminderAction({"sub-action": "null"}, "No specific action")
            action.execute()
            mock_respond.assert_called_once()

    def test_conversation_action_answer_question(self):
        """Test the answer_question method of ConversationAction."""
        action = ConversationAction({"sub-action": "answer"}, "What is AI?")
        with patch(
            "builtins.open", new_callable=mock_open, read_data="Prompt template content"
        ):
            result = action.answer_question()
            assert "Prompt template content" in result

    def test_conversation_action_small_talk(self):
        """Test the small_talk method of ConversationAction."""
        action = ConversationAction({"sub-action": "small-talk"}, "How's the weather?")
        with patch(
            "builtins.open", new_callable=mock_open, read_data="Prompt template content"
        ):
            result = action.small_talk()
            assert "Prompt template content" in result

    def test_conversation_action_respond(self):
        """Test the respond method of ConversationAction."""
        action = ConversationAction({"sub-action": "respond"}, "Tell me a joke.")
        with patch(
            "builtins.open", new_callable=mock_open, read_data="Prompt template content"
        ):
            result = action.respond()
            assert "Prompt template content" in result

    def test_conversation_action_execute(self):
        """Test the execute method of ConversationAction."""
        with patch.object(
            ConversationAction, "answer_question"
        ) as mock_answer_question:
            action = ConversationAction({"sub-action": "answer"}, "What is AI?")
            action.execute()
            mock_answer_question.assert_called_once()

        with patch.object(ConversationAction, "small_talk") as mock_small_talk:
            action = ConversationAction(
                {"sub-action": "small-talk"}, "How's the weather?"
            )
            action.execute()
            mock_small_talk.assert_called_once()

        with patch.object(ConversationAction, "respond") as mock_respond:
            action = ConversationAction({"sub-action": "respond"}, "Tell me a joke.")
            action.execute()
            mock_respond.assert_called_once()

        with patch.object(ConversationAction, "respond") as mock_respond:
            action = ConversationAction({"sub-action": "null"}, "No specific action")
            action.execute()
            mock_respond.assert_called_once()

    def test_other_action_execute(self):
        """Test the execute method of OtherAction."""
        action = OtherAction({}, "Do something else.")
        with patch("builtins.print") as mock_print:
            action.execute()
            mock_print.assert_called_once_with("Executing other action")

    def test_action_factory_calendar(self):
        """Test the action_factory function for calendar classification."""
        classifications = {"classification": "calendar"}
        question = "What meetings do I have today?"
        action = action_factory(classifications, question)
        assert isinstance(action, CalendarAction)

    def test_action_factory_reminders(self):
        """Test the action_factory function for reminders classification."""
        classifications = {"classification": "reminders"}
        question = "What reminders do I have?"
        action = action_factory(classifications, question)
        assert isinstance(action, ReminderAction)

    def test_action_factory_conversation(self):
        """Test the action_factory function for conversation classification."""
        classifications = {"classification": "conversation"}
        question = "What is AI?"
        action = action_factory(classifications, question)
        assert isinstance(action, ConversationAction)

    def test_action_factory_other(self):
        """Test the action_factory function for other classification."""
        classifications = {"classification": "other"}
        question = "Do something else."
        action = action_factory(classifications, question)
        assert isinstance(action, OtherAction)

    def test_action_factory_unknown(self):
        """Test the action_factory function for unknown classification."""
        classifications = {"classification": "unknown"}
        question = "Unknown action."
        with pytest.raises(ValueError):
            action_factory(classifications, question)
