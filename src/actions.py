"""File to handle the execution of all of the AI assistant's actions."""

import json
import google_calendar
import assistant
import navigation
import reminders
import slack_api

action_type = ""


class BaseAction:
    """Base class to handle all of the AI assistant's actions."""

    def __init__(self, classifications, question):
        """Initialize the action with the classifications."""
        self.classifications = classifications
        self.question = question

    def execute(self):
        """Execute the action."""
        raise NotImplementedError("Subclasses should implement this!")


class CalendarAction(BaseAction):
    """Class to handle the calendar actions for the AI assistant."""

    def execute(self):
        """Execute the calendar action based on the sub-action."""
        if "add" in self.classifications["sub-action"]:
            return self.add_event()
        elif "update" in self.classifications["sub-action"]:
            return self.update_event()
        elif "delete" in self.classifications["sub-action"]:
            return self.delete_event()
        elif "get-info" in self.classifications["sub-action"]:
            return self.get_event_info()
        elif "null" in self.classifications["sub-action"]:
            return self.respond()

    def add_event(self):
        """Add a calendar event."""
        print("Adding calendar event")

    def update_event(self):
        """Update a calendar event."""
        print("Updating calendar event")

    def delete_event(self):
        """Delete a calendar event."""
        print("Deleting calendar event")

    def get_event_info(self):
        """Get information about a calendar event."""
        print("Getting calendar event info")

        # Initialize the connection to the Google Calendar API.
        service = google_calendar.initialize_connection()

        # Re-initialize the classification model with the time classifier prompt.
        classification_model = assistant.initialize_classification_model(
            "src/prompt-templates/time-classifier-prompt.txt"
        )

        # Get the classifier output and tokens from the user's question.
        classifier_output, classifier_tokens = assistant.query_classifier(
            classification_model, self.question
        )

        # Convert the classifier values dictionary to a list of strings
        classifier_values_list = [
            f"{value}" for key, value in classifier_output.items()
        ]

        print("Classifier values list:", classifier_output)

        # Get the events from the Google Calendar API.
        calendar_data = google_calendar.get_time_bounded_events(
            service, classifier_output
        )

        # Save the calendar events to a json file.
        google_calendar.save_calendar_events(calendar_data)

        print("CALENDAR DATA LIST:", calendar_data)

        # Convert the calendar_data to a string for the prompt.
        calendar_data_string = "\n\n".join(
            [
                f"Event Type: {event[0]} | Event Title: {event[1]} | Start Time: {event[2]} | End Time: {event[3]} | Location: {event[4]} | Day of Event: {event[5]}"
                for event in calendar_data
            ]
        )

        # Load the calendar action prompt template.
        with open("src/prompt-templates/calendar-action-prompt.txt", "r") as file:
            prompt_template = file.read()

        # Format the calendar prompt with the calendar data.
        calendar_prompt = prompt_template.format(calendar_data=calendar_data_string)

        return calendar_prompt

    def respond(self):
        """Respond to a message."""
        print("No specific action")


class ReminderAction(BaseAction):
    """Class to handle the reminders actions for the AI assistant."""

    def execute(self):
        """Execute the reminder action based on the sub-action."""
        if "add" in self.classifications["sub-action"]:
            return self.add_reminder()
        elif "update" in self.classifications["sub-action"]:
            return self.update_reminder()
        elif "delete" in self.classifications["sub-action"]:
            return self.delete_reminder()
        elif "get-info" in self.classifications["sub-action"]:
            return self.get_reminder_info()
        elif "null" in self.classifications["sub-action"]:
            return self.respond()

    def add_reminder(self):
        """Add a reminder."""
        print("Adding reminder")

    def update_reminder(self):
        """Update a reminder."""
        print("Updating reminder")

    def delete_reminder(self):
        """Delete a reminder."""
        print("Deleting reminder")

    def get_reminder_info(self):
        """Get information about a reminder."""
        print("Getting reminder info")

    def respond(self):
        """Respond to a message."""
        print("No specific action")


class ConversationAction(BaseAction):
    """Class to handle the conversation actions for the AI assistant."""

    def execute(self):
        """Execute the conversation action based on the sub-action."""
        if "answer" in self.classifications["sub-action"]:
            return self.answer_question()
        elif "small-talk" in self.classifications["sub-action"]:
            return self.small_talk()
        elif "respond" in self.classifications["sub-action"]:
            return self.respond()
        elif "null" in self.classifications["sub-action"]:
            return self.respond()

    def answer_question(self):
        """Answer a question."""
        # Load the calendar action prompt template.
        with open("src/prompt-templates/answer-conversation-prompt.txt", "r") as file:
            prompt_template = file.read()

        # Convert the classifier values dictionary to a list of strings
        classifier_values_list = [
            f"{value}" for key, value in self.classifications.items()
        ]

        # Format the calendar prompt with the calendar data.
        answer_prompt = prompt_template.format(
            classifier_data=classifier_values_list,
        )

        return answer_prompt

    def small_talk(self):
        """Engage in small talk."""
        # Load the calendar action prompt template.
        with open("src/prompt-templates/conversation-action-prompt.txt", "r") as file:
            prompt_template = file.read()

        # Convert the classifier values dictionary to a list of strings
        classifier_values_list = [
            f"{value}" for key, value in self.classifications.items()
        ]

        # Format the calendar prompt with the calendar data.
        small_talk_prompt = prompt_template.format(
            classifier_data=classifier_values_list,
        )

        return small_talk_prompt

    def respond(self):
        """Respond to a message."""
        # Load the calendar action prompt template.
        with open("src/prompt-templates/conversation-action-prompt.txt", "r") as file:
            prompt_template = file.read()

        # Convert the classifier values dictionary to a list of strings
        classifier_values_list = [
            f"{value}" for key, value in self.classifications.items()
        ]

        # Format the calendar prompt with the calendar data.
        respond_prompt = prompt_template.format(
            classifier_data=classifier_values_list,
        )

        return respond_prompt


class OtherAction(BaseAction):
    def execute(self):
        print("Executing other action")


def action_factory(classifications, question):
    """Factory method to create action instances based on classifications."""
    if classifications["classification"] == "calendar":
        return CalendarAction(classifications, question)
    elif classifications["classification"] == "reminders":
        return ReminderAction(classifications, question)
    elif classifications["classification"] == "conversation":
        return ConversationAction(classifications, question)
    elif classifications["classification"] == "other":
        return OtherAction(classifications, question)
    else:
        raise ValueError("Unknown classification")
