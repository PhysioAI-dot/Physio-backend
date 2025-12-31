from typing import List
from sqlalchemy.orm import Session
from datetime import datetime

from inbox.models import InboxItem
from tickets.service import list_tickets
from schemas import TicketModel

def build_inbox(db: Session, practice_id: str) -> List[InboxItem]:
    """
    Echtbetrieb:
    - lädt Tickets aus der DB über den Ticket-Service
    - strikt nach practice_id (Multi-Tenancy)
    - gibt IMMER eine Liste zurück
    """
    inbox: List[InboxItem] = []

    try:
        # Hier nutzen wir den bereits existierenden Service
        tickets: List[TicketModel] = list_tickets(db, practice_id)

        for t in tickets:
            # Wir mappen das TicketModel auf das InboxItem für das Frontend
            inbox.append(
                InboxItem(
                    id=str(t.id),
                    kind="booking",
                    priority="normal",
                    status=t.status,
                    # Hier greifen wir korrekt auf das Pydantic-Untermodell zu:
                    label=f"Buchung: {t.booking_request.patient_name}" if t.booking_request else "Neue Buchung",
                    time=t.created_at.strftime("%H:%M") if t.created_at else "--:--",
                    created_at=t.created_at or datetime.utcnow(),
                )
            )

    except Exception as e:
        print(f"DEBUG inbox error: {e}")
        return []

    # Sortierung: Neueste oben
    inbox.sort(key=lambda x: x.created_at, reverse=True)
    return inbox