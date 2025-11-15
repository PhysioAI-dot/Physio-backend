from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class CallbackTicket(BaseModel):
    name: str
    phone: str
    concern: str
    urgency: str | None = None
    has_prescription: bool | None = None
    preferred_time: str | None = None
    notes: str | None = None

@app.get("/")
def root():
    return {"status": "Physio Backend live"}

@app.post("/create_ticket")
def create_ticket(ticket: CallbackTicket):
    print("📥 Neues Ticket empfangen:")
    print(ticket.dict())

    return {
        "message": "Rückruf-Ticket erfolgreich erstellt.",
        "received_data": ticket.dict()
    }
