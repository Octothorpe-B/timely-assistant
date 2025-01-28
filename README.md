# timely-assistant

[![Codecov Badge](https://codecov.io/gh/Octothorpe-B/timely-assistant/graph/badge.svg?token=2YUXJFCAKZ)](https://codecov.io/gh/Octothorpe-B/timely-assistant)

A Python-based time management bot that calculates travel times based on Google Calendar events and notifies users when to leave to arrive on time.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Setup & Configuration](#setup--configuration)
- [Running the Bot](#running-the-bot)
- [Testing](#testing)
- [Best Practices](#best-practices)
- [FAQ](#faq)

## Overview

`timely-assistant` is designed to help users manage their travel times by:

1. Integrating with Google Calendar to retrieve event details.
2. Calculating travel time to destinations.
3. Notifying users via Slack when they need to leave and arrive on time.

The bot uses the [Slack API](https://slackapi.com/) for notifications and integrates with the [Google Calendar API](https://developers.google.com/calendar) for event retrieval.

## Installation

### Requirements

- **Python 3.x**
- **Google Calendar API credentials** (see below)
- **Slack API credentials** (see below)

### Dependencies

Install all required Python packages using `make`:

```bash
make install
```

The following packages are included in `requirements.txt`:

- pytest==8.3.4
- google-auth==2.18.0
- google-auth-oauthlib==1.2.1
- google-api-python-client==2.154.0
- pytz==2022.7.1
- slack_sdk==3.27.1
- Flask==3.0.3
- langchain-core==0.3.28
- pydantic==2.10.3
- langchain-ollama==0.2.2
- langchain==0.3.13
- pytest-cov==6.0.0

## Setup & Configuration

### Slack API Credentials

To integrate with Slack, you need to create an app and obtain the following credentials:

1. **Bot Token**: Used for sending messages.
2. **App Token**: Used for socket mode connections.

Set these environment variables before running the bot:

```bash
export SLACK_BOT_TOKEN="your_bot_token"
export SLACK_APP_TOKEN="your_app_token"
```

You can create your Slack app and generate tokens at the [Slack API OAuth Page](https://slackapi.com/).

### Google Calendar Setup

Create a project in the Google Cloud Console. Enable the Google Calendar API for your project. Generate API credentials (JSON key file) and download it to your project directory.

## Running the Bot

The bot can be run using the following command:

```bash
make run
```

### Main Functionality

- **Main Entry Point**: `main.py`
  - Connects to Slack and initializes the bot.
  - Handles events and notifications based on Google Calendar data.

## Testing

To test the application, run:

```bash
make test
```

This will execute unit tests using pytest. For more information on testing, refer to the pytest documentation.

## FAQ

Coming soon!

## Future Enhancements

- Add deployment instructions (coming soon).
- Include more detailed configuration options for classifiers and AI models.
- Implement user authentication for multiple users or teams.