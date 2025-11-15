from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

class CallbackTicket(BaseModel):
    name: str
    phone: str
    concern: str
    urgency: str | None = None
    has_prescription: bool | None = None
    preferred_time: str | None = None
    notes: str | None = None

tickets = []

@app.get("/")
def root():
    return {"status": "Physio Backend live"}

@app.post("/callback-ticket")
def create_ticket(ticket: CallbackTicket):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "name": ticket.name,
        "phone": ticket.phone,
        "concern": ticket.concern,
        "urgency": ticket.urgency,
        "has_prescription": ticket.has_prescription,
        "preferred_time": ticket.preferred_time,
        "notes": ticket.notes
    }
    tickets.append(entry)
    print("NEUES TICKET:", entry)
    return {"status": "ticket_created", "data": entry}
