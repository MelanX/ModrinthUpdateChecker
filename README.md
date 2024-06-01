# Modrinth Update Checker

This Python application helps you to automatically check updates for projects from Modrinth.
If there are any updates, a notification will be sent to a Discord webhook.

## Usage

1. Make sure you have Python 3.12 installed on your system.
2. Install the `requests` library with pip install requests.
3. A webhook URL should be passed as a command-line argument when running the program. If the program is run without
   a webhook URL it will exit with an error message.
4. The `projects.txt` file containing the list of projects is necessary for the program to run. The program will check
   each project for updates.
5. This script caches the last checked versions in a file called `last_checked.json`. It will be created on first run.
   Not yet processed projects will not generate a notification for each version, only after first run.
