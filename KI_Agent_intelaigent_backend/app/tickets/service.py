# app/tickets/service.py

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from typing import List, Optional

from app.database_models import Ticket
from app.schemas import TicketModel, TicketStatus


def from_db_ticket_to_pydantic(db_ticket: Ticket) -> TicketModel:
    data = db_ticket.data or {}
    ticket = TicketModel.parse_obj(data)
    ticket.ticket_id = str(db_ticket.id)
    ticket.practice_id = db_ticket.practice_id
    ticket.status = db_ticket.status
    ticket.created_at = db_ticket.created_at
    return ticket


def create_ticket(db: Session, ticket_model: TicketModel) -> Ticket:
    db_ticket = Ticket(
        practice_id=ticket_model.practice_id,
        status=ticket_model.status,
        created_at=datetime.utcnow()
    )
    db_ticket.set_data(ticket_model)

    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket


def get_ticket(db: Session, ticket_id: int, practice_id: str) -> Optional[TicketModel]:
    db_ticket = (
        db.query(Ticket)
        .filter(Ticket.id == ticket_id, Ticket.practice_id == practice_id)
        .first()
    )
    if not db_ticket:
        return None
    return from_db_ticket_to_pydantic(db_ticket)


def list_tickets(
    db: Session,
    practice_id: str,
    status: Optional[TicketStatus] = None
) -> List[TicketModel]:

    query = db.query(Ticket).filter(Ticket.practice_id == practice_id)

    if status:
        query = query.filter(Ticket.status == status)

    tickets = query.all() or []

    return [from_db_ticket_to_pydantic(t) for t in tickets]


def update_ticket_status(
    db: Session,
    ticket_id: int,
    practice_id: str,
    new_status: TicketStatus
) -> Optional[TicketModel]:

    db_ticket = (
        db.query(Ticket)
        .filter(Ticket.id == ticket_id, Ticket.practice_id == practice_id)
        .first()
    )
    if not db_ticket:
        return None

    db_ticket.status = new_status
    db.commit()
    db.refresh(db_ticket)
    return from_db_ticket_to_pydantic(db_ticket)


def delete_ticket(db: Session, ticket_id: int, practice_id: str) -> bool:
    db_ticket = (
        db.query(Ticket)
        .filter(Ticket.id == ticket_id, Ticket.practice_id == practice_id)
        .first()
    )
    if not db_ticket:
        return False

    db.delete(db_ticket)
    db.commit()
    return True
