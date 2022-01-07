import dataclasses
from datetime import datetime
from datetime import timedelta
import json
import os
import sys
from typing import List

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from scheduler.scheduler_config import Time

from logger import get_logger
from metrics import Metrics

logger = get_logger()
metrics = Metrics()

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
CREDENTIALS_FILE = os.path.join(sys.path[0], "scheduler/credentials.json")
TOKEN_FILE = os.path.join(sys.path[0], "scheduler/token.json")


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)

class CalendarSync:

    def get_schedule(self, events) -> List[Time]:
        schedule = []
        for event in events:
            start = datetime.fromisoformat(event['start'].get('dateTime', event['start'].get('date')))
            summary = event['summary']
            if "Boiler intensity:" in summary:
                intensity = summary.split('intensity:')[1]
                schedule.append(Time(start.hour, start.minute, int(intensity)))
        return schedule

    def run(self):
        metrics.incr("calendar_sync.start")
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
                logger.info('No upcoming events found.')
                return

            schedule = self.get_schedule(events)
            file = os.path.join(sys.path[0], "scheduler/calendar_config.json")
            old_schedule = None
            try:
                with open(file, "r") as f:
                    lines = f.readlines()
                    old_schedule = json.loads('\n'.join(lines))
            except:
                pass
            if json.dumps(schedule, sort_keys=True, cls=EnhancedJSONEncoder) != json.dumps(old_schedule, sort_keys=True, cls=EnhancedJSONEncoder):
                metrics.event("schedule change", "by calendar", alert_type="info")
                with open(file, "w") as f:
                    f.write(json.dumps(schedule, indent=4, cls=EnhancedJSONEncoder))
                
        except HttpError as error:
            metrics.incr("calendar_sync.error")
            logger.info('An error occurred: %s' % error)

    metrics.incr("calendar_sync.end")


if __name__ == '__main__':
    CalendarSync().run()