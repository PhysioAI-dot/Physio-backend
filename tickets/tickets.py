from schemas import CallbackTicket
from datetime import datetime
from tickets.callback_store import save_callback


def save_ticket(ticket):
    ...


def create_callback_ticket(
    from_number: str,
    reason: str = "Voice Callback"
) -> CallbackTicket:
    ticket = CallbackTicket(
        phone=from_number,
        reason=reason,
        created_at=datetime.utcnow()
    )

    save_ticket(ticket)
    save_callback(ticket)
    return ticket
