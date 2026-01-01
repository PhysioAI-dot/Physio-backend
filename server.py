# -------------------------------------------------
# Standard Imports
# -------------------------------------------------
from fastapi import FastAPI, HTTPException, Depends, Query, Request, Body
from typing import Optional
from sqlalchemy.orm import Session
from typing import List, Union
from datetime import date
from statistics import mean
import logging

# -------------------------------------------------
# Logging-Konfiguration für Render
# -------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("twilio-agent")

# Router
from voice.router import router as voice_router
from dashboard.router import router as dashboard_router
from tickets.router import router as tickets_router
from inbox.router import router as inbox_router

# Twilio Handler
from voice.twilio_handler import handle_twilio_webhook, handle_twilio_status
from voice.test_handler import test_voice_webhook

# -------------------------------------------------
# Datenbank
# -------------------------------------------------
from database import engine, Base, get_db
import database_models  # wichtig für SQLAlchemy Metadata
Base.metadata.create_all(bind=engine)

# -------------------------------------------------
# Schemas
# -------------------------------------------------
from schemas import (
    BookingRequest,
    SlotModel,
    TicketModel,
    CallbackTicket,
    PracticeId,
    TicketStatus,
)

# Services
from slots.dispatcher import get_slots_for_practice
from booking.booking_flow import process_booking_request
from calendar.calendar_service import CalendarService
from tickets.service import list_tickets

# -------------------------------------------------
# App Initialisierung
# -------------------------------------------------
app = FastAPI(
    title="IntelAiGent Backend",
    description="Modulares KI-Agent Backend – Version B",
    version="1.0.0",
)

app.include_router(tickets_router)
app.include_router(dashboard_router)
app.include_router(voice_router)
app.include_router(inbox_router)

calendar_service = CalendarService()

# -------------------------------------------------
# Twilio Webhooks
# -------------------------------------------------
@app.post("/voice/twilio-webhook")
async def twilio_webhook(request: Request):
    """Twilio Webhook für eingehende Voice-Anrufe"""
    return await handle_twilio_webhook(request)

@app.post("/voice/status")
async def twilio_status(request: Request):
    """Twilio Status Callback für Call-Events"""
    return await handle_twilio_status(request)

# -------------------------------------------------
# KOSTENLOSER TEST-ENDPOINT (ohne echte Anrufe)
# -------------------------------------------------
@app.post("/voice/test")
async def test_voice_post(
    text: str,
    from_number: str = "+491234567890",
    practice_id: str = "physio_default_20min"
):
    """
    🆓 KOSTENLOSER Test-Endpoint für Voice-Anrufe
    
    Simuliert Twilio Webhooks OHNE echte Anrufe!
    
    Nutzung:
    POST /voice/test?text=Ich möchte einen Termin buchen&from_number=+491234567890
    
    Oder mit JSON Body:
    POST /voice/test
    {
        "text": "Ich möchte einen Termin buchen",
        "from_number": "+491234567890",
        "practice_id": "physio_default_20min"
    }
    """
    return await test_voice_webhook(text, from_number, practice_id)

@app.get("/voice/test")
async def test_voice_get(
    text: str,
    from_number: str = "+491234567890",
    practice_id: str = "physio_default_20min"
):
    """
    🆓 KOSTENLOSER Test-Endpoint (GET) für schnelles Testen im Browser
    
    Beispiel:
    https://deine-url.onrender.com/voice/test?text=Ich möchte einen Termin buchen
    """
    return await test_voice_webhook(text, from_number, practice_id)

# -------------------------------------------------
# Health Check
# -------------------------------------------------
@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "IntelAiGent Backend läuft.",
    }

# -------------------------------------------------
# Slots abrufen
# -------------------------------------------------
@app.get("/slots", response_model=List[SlotModel])
def get_slots(
    practice_id: PracticeId,
    date_str: str,
):
    try:
        for_date = date.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Ungültiges Datumsformat")

    return get_slots_for_practice(
        practice_id=practice_id,
        for_date=for_date,
    )

# -------------------------------------------------
# Booking auslösen
# -------------------------------------------------
from tickets.service import create_ticket

@app.post("/book", response_model=Union[TicketModel, CallbackTicket])
def book_appointment(
    booking_request: BookingRequest,
    db: Session = Depends(get_db),
):
    result = process_booking_request(booking_request)

    # 🔥 NUR WENN ES EIN TICKET IST → IN DB SPEICHERN
    if isinstance(result, TicketModel):
        create_ticket(db=db, ticket_model=result)

        if result.slot:
            calendar_service.create_event(
                title=f"Termin – {booking_request.patient_name}",
                start=result.slot.start_time,
                end=result.slot.end_time,
                description="Gebucht über IntelAiGent",
            )

    return result


# ---------------------------------------------------------
# DASHBOARD – SUMMARY (DB-basiert & mandantenfähig)
# ---------------------------------------------------------
@app.get("/api/dashboard/summary")
def dashboard_summary(
    practice_id: PracticeId = Query(..., description="Mandanten-ID"),
    db: Session = Depends(get_db),
):
    tickets = list_tickets(db=db, practice_id=practice_id.value)
    today = date.today()

    tickets_today = [
        t for t in tickets
        if t.created_at and t.created_at.date() == today
    ]

    total_today = len(tickets_today)

    open_callbacks = [
        t for t in tickets_today
        if t.status == TicketStatus.CALLBACK
    ]

    successful = [
        t for t in tickets_today
        if t.status == TicketStatus.BOOKED
    ]

    success_rate = round((len(successful) / total_today) * 100) if total_today > 0 else 0

    response_times = []
    for t in successful:
        if t.slot and t.slot.start_time:
            delta = t.slot.start_time - t.created_at
            minutes = int(delta.total_seconds() / 60)
            if minutes >= 0:
                response_times.append(minutes)

    avg_response_time = round(mean(response_times)) if response_times else None

    return {
        "date": today.isoformat(),
        "tickets_today": total_today,
        "open_callbacks": len(open_callbacks),
        "success_rate": success_rate,
        "avg_response_time_minutes": avg_response_time,
    }
