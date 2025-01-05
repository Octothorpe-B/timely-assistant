# timely-assistant

[![codecov](https://codecov.io/gh/Octothorpe-B/timely-assistant/graph/badge.svg?token=2YUXJFCAKZ)](https://codecov.io/gh/Octothorpe-B/timely-assistant)

Time management bot that calculates and lets you know when to get ready and leave for a place and arrive there on time.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Running the Bot](#running-the-bot)

## Overview

timely-assistant is a Python-based application designed to help users manage their travel times based on Google Calendar events. It retrieves your calendar events, calculates the travel time to your destination, and notifies you when to get ready and leave to arrive on time.

## Installation

To run timely-assistant, you will need:

1. **Python 3.x**: Ensure Python is installed on your system.
2. **Google API Credentials**: Obtain client ID and client secret from the Google Developer Console for accessing the Google Calendar API.
3. **Dependencies**: Install required Python packages using `pip`.

### Prerequisites

Ensure you have the following prerequisites:

- Python 3.x
- `google-auth`, `google-auth-oauthlib`, `google-auth-httplib2`, and `google-api-python-client` installed.

You can install these dependencies by running:

```sh
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### Setting Up Google API Credentials

1. Go to the Google Developer Console.
2. Create a new project or select an existing one.
3. Navigate to "APIs & Services" > "OAuth consent screen" and configure it according to your requirements.
4. Enable the Google Calendar API under "APIs & Services" > "Library".
5. Go to "Credentials" and create credentials of type "OAuth client ID". Choose Other as the application type and give a name for your application.
6. Download the JSON file and rename it to `credentials.json`.

## Running the Bot

1. Navigate to the Project Directory:
`cd path/to/timely-assistant`

2. Run the Application:
`python src/main.py`

3. Follow the Instructions:

- The script will prompt you to authorize access to your Google Calendar.
- Follow the on-screen instructions to complete the OAuth 2.0 authorization flow.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
