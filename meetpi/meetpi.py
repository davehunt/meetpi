"""Google Calendar meeting status indicator for Raspberry Pi + Blinkt."""

import argparse
from datetime import datetime
import os.path
import pickle
import time

try:
    import blinkt

    blinkt_present = True
except ImportError:
    blinkt_present = False

from dateutil.parser import isoparse
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


COLOURS = {"OUT OF OFFICE": (0, 0, 0), "BUSY": (255, 0, 0), "FREE": (0, 255, 0)}
OFFICE_DAYS = range(0, 5)
OFFICE_HOURS = range(9, 20)


def get_credentials() -> dict:
    """Get credentials from user or cache."""
    credentials = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes the first time.
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            credentials = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", "https://www.googleapis.com/auth/calendar.readonly"
            )
            credentials = flow.run_console()
        # Save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(credentials, token)
    return credentials


def get_today() -> datetime:
    """Return current day."""
    return datetime.today()


def get_events(calendar_id: str) -> list:
    """Get events from the calendar."""
    events = (
        service.events()
        .list(
            calendarId=calendar_id,
            timeMin=datetime.utcnow().isoformat() + "Z",
            maxResults=5,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    return [e for e in events.get("items", []) if valid_event(e)]


def started(event: dict) -> bool:
    """Return if the event has started."""
    datestr = event["start"].get("dateTime", event["start"].get("date"))
    delta = isoparse(datestr).replace(tzinfo=None) - datetime.now()
    return delta.days < 0


def attending(event: dict) -> bool:
    """Return if user is attending the event."""
    for attendee in event.get("attendees", []):
        if attendee.get("self") and attendee.get("responseStatus") == "accepted":
            # At least one attendee, and calendar owner is attending
            return True
    return False


def valid_event(event: dict) -> bool:
    """Return if the event is valid."""
    return started(event) and attending(event)


def office_hours() -> bool:
    """Return office hours status."""
    today = get_today()
    print(f"Day of the week: {today.weekday()}\nHour of the day: {today.hour}")
    return today.weekday() in OFFICE_DAYS and today.hour in OFFICE_HOURS


def get_status(calendar_id: str) -> str:
    """Return meeting status."""
    if office_hours():
        events = get_events(calendar_id)
        print(f"There are {len(events)} event(s) on the calendar")
        status = "BUSY" if len(events) > 0 else "FREE"
    else:
        status = "OUT OF OFFICE"
    print(f"Status: {status}")
    return status


def set_blinkt(colour: tuple, brightness: float):
    """Set all Blinkt pixels to a singe colour."""
    if blinkt_present:
        print(f"Setting blinkt to: {colour}")
        blinkt.set_all(*colour, brightness)
        blinkt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("calendar", help="calendar id to use for meeting status")
    parser.add_argument(
        "--brightness", help="set brightness for Blinkt", type=float, default=0.2
    )
    parser.add_argument(
        "--query-delay",
        help="delay between querying the calendar",
        type=int,
        default=10,
    )
    args = parser.parse_args()

    if blinkt_present:
        blinkt.set_clear_on_exit(True)
    credentials = get_credentials()
    service = build("calendar", "v3", credentials=credentials)
    last_check = None
    while True:
        if last_check is None or time.monotonic() >= last_check + args.query_delay:
            status = get_status(args.calendar)
            set_blinkt(COLOURS[status], args.brightness)
            last_check = time.monotonic()
