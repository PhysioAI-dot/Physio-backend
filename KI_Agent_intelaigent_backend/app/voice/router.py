from fastapi import APIRouter
from datetime import date

# Korrekte Imports aus schemas
from app.schemas import VoicePayload, PracticeId, TicketModel
from app.booking.booking_flow import auto_book_from_voice
from app.intents.voice_intent import detect_intent, VoiceIntent
from app.tickets.tickets import create_callback_ticket

router = APIRouter(prefix="/voice", tags=["Voice"])

@router.post("")
def voice_webhook(payload: VoicePayload):
    intent = detect_intent(payload.text)

    # 1. CALLBACK
    if intent == VoiceIntent.CALLBACK:
        ticket = create_callback_ticket(
            from_number=payload.from_number,
            reason=payload.text,
        )
        return {
            "intent": intent,
            "status": "callback_created",
            "ticket_id": ticket.ticket_id,
        }

    # 2. BOOKING
    if intent == VoiceIntent.BOOKING:
        ticket = auto_book_from_voice(
            practice_id=PracticeId.PHYSIO_DEFAULT_20,
            patient_name="Unbekannt (Voice)",
            patient_phone=payload.from_number,
            for_date=date.today(),
        )

        # Überprüfung, ob ein echtes Ticket (Buchung) oder ein Fallback (Callback) erstellt wurde
        if isinstance(ticket, TicketModel):
            return {
                "intent": intent,
                "status": "booked",
                "ticket_id": ticket.ticket_id,
                "slot": {
                    "start": ticket.slot.start_time,
                    "end": ticket.slot.end_time,
                },
            }

        # Falls kein Slot frei war, wurde automatisch ein Callback erstellt
        return {
            "intent": intent,
            "status": "callback_created",
            "ticket_id": ticket.ticket_id,
            "message": "Kein Slot verfügbar – Rückruf erstellt",
        }

    # 3. CANCEL
    if intent == VoiceIntent.CANCEL:
        return {
            "intent": intent,
            "status": "cancel_intent_detected",
            "message": "Absage erkannt – Status-Update folgt",
        }

    # 4. FALLBACK (Unbekannter Intent)
    return {
        "intent": intent,
        "status": "unknown_intent",
        "message": "Intent nicht eindeutig",
    }


    # CANCEL
    if intent == VoiceIntent.CANCEL:
        return {
            "intent": intent,
            "status": "cancel_intent_detected",
            "message": "Absage erkannt – Status-Update folgt",
        }

    # FALLBACK
    return {
        "intent": intent,
        "status": "unknown_intent",
        "message": "Intent nicht eindeutig",
    }
