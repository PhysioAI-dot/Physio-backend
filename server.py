from fastapi import FastAPI
from fastapi.responses import Response
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

# -------------------------------
# Callback-Ticket Modell
# -------------------------------

class CallbackTicket(BaseModel):
    name: str
    phone: str
    concern: str
    urgency: str | None = None
    has_prescription: bool | None = None
    preferred_time: str | None = None
    notes: str | None = None

# Simulierter Speicher
tickets = []

@app.get("/")
def root():
    return {"status": "Physio Backend live"}

@app.post("/create_ticket")
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
    print("🔥 NEUES TICKET:", entry)
    return {"message": "Rückruf-Ticket erfolgreich erstellt.", "received_data": ticket.dict()}

# -------------------------------
# Twilio Voice Webhook
# -------------------------------

@app.api_route("/voice", methods=["GET", "POST"])
async def voice_webhook():
    twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Marlene-Neural">
        Hallo, ich bin Ihr KI Telefonassistent. Wie kann ich Ihnen helfen?
    </Say>
</Response>"""
    return Response(content=twiml, media_type="application/xml")

