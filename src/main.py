"""
Main program file to manage the running of Timely.
"""

import google_calendar
import events


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

    # 2. TODO: Implement code to convert the home address and destination address into latitude and longitude.

    # 3. TODO: Implement code to calculate the travel time to the destination.

    # 4. TODO: Implement logic to notify the user when to best start getting ready and when to leave.
