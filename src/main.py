"""
Main program file to manage the running of Timely.
"""

import google_calendar


def obtain_calendar():
    """Function to get the user's calendar to obtain their events and their locations."""


if __name__ == "__main__":
    # 1. Initialize connection with Google Calendar API and return the service object that connects the program to the API.
    service = google_calendar.initialize_connection()

    # TODO: Initialize the connection with the Google Calendar API.
    calendar_events = google_calendar.get_next_24hr_events(service)

    # Output the calendar events for the next 24 hours to the terminal.
    print(calendar_events)

    # TODO: Obtain a list of the current day's calendar events that take place at a specific time and at a specific location.

    # TODO: Save the obtained calendar event information and location information for later use.

    # 2. TODO: Implement code to convert the home address and destination address into latitude and longitude.

    # 3. TODO: Implement code to calculate the travel time to the destination.

    # 4. TODO: Implement logic to notify the user when to best start getting ready and when to leave.
