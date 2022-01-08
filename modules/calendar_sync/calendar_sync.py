from datetime import datetime, timedelta
import os
import sys
from typing import List

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from data_stores.schedule.schedule_data_store import ScheduleDataStore, Time

from utils.logger import get_logger
from utils.metrics import Metrics

logger = get_logger()
metrics = Metrics()

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
CREDENTIALS_FILE = os.path.join(sys.path[0], "secrets/credentials.json")
TOKEN_FILE = os.path.join(sys.path[0], "secrets/token.json")
TIME_ZONE = 2


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
            schedule_ds = ScheduleDataStore()
            old_schedule = schedule_ds.load_schedule()
            if not old_schedule or schedule.to_json() != old_schedule.to_json():
                metrics.event("schedule change", "by calendar", alert_type="info")
                new_schedule = [time.plus_hours(0 - TIME_ZONE) for time in schedule]
                schedule_ds.save_schedule(new_schedule)
                
        except HttpError as error:
            metrics.incr("calendar_sync.error")
            logger.info('An error occurred: %s' % error)

    metrics.incr("calendar_sync.end")