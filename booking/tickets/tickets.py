import json
from pathlib import Path
from typing import List, Union

from schemas import TicketModel, CallbackTicket



# -------------------------------------------------
# Konfiguration
# -------------------------------------------------

DATA_DIR = Path(__file__).resolve().parent.parent
TICKETS_FILE = DATA_DIR / "tickets.json"


# -------------------------------------------------
# Hilfsfunktionen
# -------------------------------------------------

def _load_raw_tickets() -> List[dict]:
    if not TICKETS_FILE.exists():
        return []

    with open(TICKETS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_raw_tickets(data: List[dict]) -> None:
    with open(TICKETS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# -------------------------------------------------
# Öffentliche API
# -------------------------------------------------

def save_ticket(
    ticket: Union[TicketModel, CallbackTicket],
) -> None:
    """
    Speichert ein Ticket (Termin oder Callback) persistent.
    """

    tickets = _load_raw_tickets()
    tickets.append(ticket.model_dump())
    _save_raw_tickets(tickets)


def load_all_tickets() -> List[dict]:
    """
    Lädt alle Tickets (roh, für Admin / Debug).
    """
    return _load_raw_tickets()
