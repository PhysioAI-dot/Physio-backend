from fastapi import APIRouter, HTTPException
from typing import List

from app.schemas import TicketModel, TicketStatus
from app.tickets.service import (
    create_ticket,
    get_ticket,
    list_tickets,
    update_ticket_status,
    delete_ticket,
)

# Standard-Router ohne versteckte Flags
router = APIRouter(prefix="/tickets", tags=["Tickets"])

# --- READ (List) ---
@router.get("", response_model=List[TicketModel])
@router.get("/", response_model=List[TicketModel])
def api_list_tickets():
    """Akzeptiert /tickets und /tickets/ ohne Redirect für maximale Stabilität."""
    return list_tickets()

# --- READ (Single) ---
@router.get("/{ticket_id}", response_model=TicketModel)
def api_get_ticket(ticket_id: str):
    ticket = get_ticket(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket nicht gefunden")
    return ticket

# --- CREATE ---
@router.post("", response_model=TicketModel)
@router.post("/", response_model=TicketModel)
def api_create_ticket(ticket: TicketModel):
    """Erlaubt Ticket-Erstellung über beide Pfad-Varianten."""
    return create_ticket(ticket)

# --- UPDATE ---
@router.patch("/{ticket_id}/status", response_model=TicketModel)
def api_update_status(ticket_id: str, status: TicketStatus):
    ticket = update_ticket_status(ticket_id, status)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket nicht gefunden")
    return ticket

# --- DELETE ---
@router.delete("/{ticket_id}")
def api_delete_ticket(ticket_id: str):
    if not delete_ticket(ticket_id):
        raise HTTPException(status_code=404, detail="Ticket nicht gefunden")
    return {"deleted": True}