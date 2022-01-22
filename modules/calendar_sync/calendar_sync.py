from datetime import datetime, timedelta
import os
from typing import List

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from data_stores.schedule.schedule_data_store import ScheduleDataStore, Time

from metrics.metrics import Metrics
from utils.logger import get_logger
from utils.secrets import SECRETS_PATH

logger = get_logger()
metrics = Metrics()

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
CREDENTIALS_FILE = os.path.join(SECRETS_PATH, "credentials.json")
TOKEN_FILE = os.path.join(SECRETS_PATH, "token.json")
TIME_ZONE = 2


class CalendarSync:

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

            schedule_ds = ScheduleDataStore()

            kill_switch = self.has_kill_switch(events)
            if kill_switch:
                schedule_ds.save_schedule([])
                return

            schedule = self.get_schedule(events)

            old_schedule = schedule_ds.load_schedule()
            if not old_schedule or schedule != old_schedule:
                logger.info(f'New schedule: {schedule}')
                metrics.incr("calendar_sync.schedule_changed")
                schedule_ds.save_schedule(schedule)
                
        except HttpError as error:
            metrics.incr("calendar_sync.error")
            logger.info('An error occurred: %s' % error)

        metrics.incr("calendar_sync.end")

    def get_schedule(self, events) -> List[Time]:
        schedule = []
        for event in events:
            start = datetime.fromisoformat(event['start'].get('dateTime', event['start'].get('date')))
            summary = event['summary']
            if "boiler intensity:" in summary.lower():
                intensity = summary.split('intensity:')[1]
                schedule.append(Time(start.hour, start.minute, int(intensity)))
        return schedule

    def has_kill_switch(self, events) -> bool:
        return any("kill switch" in event['summary'].lower() for event in events)