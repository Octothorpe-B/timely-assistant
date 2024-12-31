"""File to handle the execution of all of the AI assistant's actions."""

import json
import google_calendar
import assistant
import navigation
import reminders
import slack_api


class BaseAction:
    """Base class to handle all of the AI assistant's actions."""

    def __init__(self, classifications):
        """Initialize the action with the classifications."""
        self.classifications = classifications

    def execute(self):
        """Execute the action."""
        raise NotImplementedError("Subclasses should implement this method.")


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

        # Get the next 24 hours of events from the Google Calendar API.
        google_calendar.get_next_24hr_events(service)

        # Open the calendar.json file which was just updated to have the latest events for today and read the data.
        with open("src/data/calendar.json", "r") as calendar:
            calendar_data = json.load(calendar)

        # Convert the calendar data from JSON to a string.
        calendar_data_string = json.dumps(calendar_data)

        calendar_data_string = (
            "This is the user's calendar for today. When completing your answer please format using a numbered list for the calendar events. " + str(calendar_data_string)
        )

        print("calendar_data_string: ", calendar_data_string)

        return calendar_data_string


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

    def answer_question(self):
        """Answer a question."""
        print("Answering question")

    def small_talk(self):
        """Engage in small talk."""
        print("Small talk")

    def respond(self):
        """Respond to a message."""
        print("Responding")


class OtherAction(BaseAction):
    def execute(self):
        print("Executing other action")


def action_factory(classifications):
    """Factory method to create action instances based on classifications."""
    if "calendar" in classifications["classification"]:
        return CalendarAction(classifications)
    elif "reminders" in classifications["classification"]:
        return ReminderAction(classifications)
    elif "conversation" in classifications["classification"]:
        return ConversationAction(classifications)
    elif "other" in classifications["classification"]:
        return OtherAction(classifications)
    else:
        raise ValueError("Unknown classification")


# Example usage
if __name__ == "__main__":
    classifications = {"classification": "reminders", "sub-action": "answer"}
    action = action_factory(classifications)
    action.execute()
