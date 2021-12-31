from datetime import datetime
from datetime import timedelta
import json
import os
import sys

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
CREDENTIALS_FILE = os.path.join(sys.path[0], "credentials.json")
TOKEN_FILE = os.path.join(sys.path[0], "token.json")


def main():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)

        now = datetime.utcnow().isoformat() + 'Z'
        tomorrow = (datetime.utcnow() + timedelta(days=1)).isoformat() + 'Z'
        events_result = service.events().list(calendarId='8jilgvcemb2v9vj3bgsmcg850c@group.calendar.google.com', timeMin=now, timeMax=tomorrow, singleEvents=True, orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            return

        schedule = []
        for event in events:
            start = datetime.fromisoformat(event['start'].get('dateTime', event['start'].get('date')))
            summary = event['summary']
            if "Boiler intensity:" in summary:
                intensity = summary.split('intensity:')[1]
                schedule.append({
                    'hour': int(start.hour),
                    'minute': int(start.minute),
                    'intensity': int(intensity),
                })
        file = os.path.join(sys.path[0], "calendar_config.json")
        if schedule:
            with open(file, "w") as f:
                f.write(json.dumps(schedule, indent=4))
        else:
            os.remove(file)
            

    except HttpError as error:
        print('An error occurred: %s' % error)


if __name__ == '__main__':
    main()
