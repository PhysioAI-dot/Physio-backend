from datetime import datetime
from typing import Optional


# Google Libraries (werden später installiert)
# from google.oauth2 import service_account
# from googleapiclient.discovery import build


# -------------------------------------------------
# Konfiguration (später aus .env)
# -------------------------------------------------

GOOGLE_CALENDAR_ID = "primary"
GOOGLE_SCOPES = ["https://www.googleapis.com/auth/calendar"]


# -------------------------------------------------
# Calendar Service
# -------------------------------------------------

class CalendarService:
    """
    Gekapselter Zugriff auf Google Calendar.
    Auth & Client-Erstellung sind bewusst ausgelagert.
    """

    def __init__(self):
        self._service = None

    def _get_service(self):
        """
        Lazy Init des Google Calendar Clients.
        """
        if self._service is not None:
            return self._service

        # TODO (Schritt 8): echte Auth über Service Account
        # credentials = service_account.Credentials.from_service_account_file(
        #     "service_account.json",
        #     scopes=GOOGLE_SCOPES,
        # )
        # self._service = build("calendar", "v3", credentials=credentials)

        # Platzhalter für jetzt
        self._service = "MOCK_CALENDAR_CLIENT"
        return self._service

    def create_event(
        self,
        title: str,
        start: datetime,
        end: datetime,
        description: Optional[str] = None,
    ) -> dict:
        """
        Erstellt ein Kalender-Event.
        Gibt Event-Daten zurück (oder später Event-ID).
        """

        service = self._get_service()

        # MOCK – wird in Schritt 8 ersetzt
        event = {
            "summary": title,
            "start": start.isoformat(),
            "end": end.isoformat(),
            "description": description,
            "calendar": GOOGLE_CALENDAR_ID,
        }

        # Später:
        # created_event = service.events().insert(
        #     calendarId=GOOGLE_CALENDAR_ID,
        #     body=event,
        # ).execute()
        # return created_event

        return event
