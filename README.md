# Modrinth Update Checker

This Python application helps you to automatically check updates for projects from Modrinth.
If there are any updates, a notification will be sent to a Discord webhook.

## Usage

### Prerequisites

1. Install Python 3.12
2. `pip install -r requirements.txt`

### Run script

`python main.py <discord_webhook_url> <projects_file>`
The file is a text file with the modrinth slug of each mod on Modrinth in each line.

### Cache

When running, it'll create a file called `last_checked.json` which contains all versions for each project which will not
be checked since they were already checked, or were already present on first run.