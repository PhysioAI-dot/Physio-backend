from fastapi import FastAPI, Form
from fastapi.responses import Response
from pydantic import BaseModel

app = FastAPI()

# ----------------------------------------------------
# Callback Ticket Model
# ----------------------------------------------------
class CallbackTicket(BaseModel):
    name: str
    phone: str
    concern: str
    urgency: str | None = None
    has_prescription: bool | None = None
    preferred_time: str | None = None
    notes: str | None = None


# ----------------------------------------------------
# Root Endpoint
# ----------------------------------------------------
@app.get("/")
def root():
    return {"status": "Physio Backend live"}


# ----------------------------------------------------
# Callback Ticket Endpoint
# ----------------------------------------------------
@app.post("/create_ticket")
def create_ticket(ticket: CallbackTicket):
    print("📩 Neues Ticket empfangen:")
    print(ticket.dict())

    return {
        "message": "Rückruf-Ticket erfolgreich erstellt.",
        "received_data": ticket.dict()
    }


# ----------------------------------------------------
# 🔥 TWILIO VOICE ENDPOINT
# ----------------------------------------------------
@app.post("/voice")
async def voice_endpoint(
    From: str = Form(...),
    To: str = Form(...)
):
    twiml_response = """
    <?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Say voice="alice" language="de-DE">
            Hallo, hier spricht der KI Voice Agent von Sascha.
            Die Verbindung zum Physio Backend steht erfolgreich.
        </Say>
    </Response>
    """

    return Response(content=twiml_response, media_type="application/xml")
