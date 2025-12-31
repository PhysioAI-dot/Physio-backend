from fastapi import APIRouter
from datetime import date
from typing import List, Dict

from app.tickets.service import list_tickets
from app.schemas import TicketStatus, TicketModel


router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats")
def dashboard_stats() -> Dict[str, int]:
    tickets = list_tickets()

    stats = {
        "total": len(tickets),
        "open": 0,
        "booked": 0,
        "callback": 0,
        "closed": 0,
    }

    for ticket in tickets:
        if ticket.status == TicketStatus.OPEN:
            stats["open"] += 1
        elif ticket.status == TicketStatus.BOOKED:
            stats["booked"] += 1
        elif ticket.status == TicketStatus.CALLBACK:
            stats["callback"] += 1
        elif ticket.status == TicketStatus.CLOSED:
            stats["closed"] += 1

    return stats


@router.get("/today", response_model=List[TicketModel])
def dashboard_today():
    today = date.today()
    tickets = list_tickets()

    today_tickets = [
        ticket for ticket in tickets
        if ticket.created_at.date() == today
    ]

    return today_tickets

