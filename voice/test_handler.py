"""
KOSTENLOSER TEST-ENDPOINT für Voice-Anrufe
Simuliert Twilio Webhooks OHNE echte Anrufe
"""
from fastapi import Request
from fastapi.responses import Response, JSONResponse
from datetime import date
from typing import Optional

from schemas import PracticeId, TicketModel
from booking.booking_flow import auto_book_from_voice
from intents.voice_intent import detect_intent, VoiceIntent
from tickets.tickets import create_callback_ticket


async def test_voice_webhook(
    text: str,
    from_number: str = "+491234567890",
    practice_id: str = "physio_default_20min"
):
    """
    KOSTENLOSER Test-Endpoint für Voice-Anrufe
    
    Nutzung:
    POST /voice/test?text=Ich möchte einen Termin buchen&from_number=+491234567890
    
    Oder mit JSON:
    POST /voice/test
    {
        "text": "Ich möchte einen Termin buchen",
        "from_number": "+491234567890",
        "practice_id": "physio_default_20min"
    }
    """
    
    # Defaults
    if not from_number:
        from_number = "+491234567890"
    if not practice_id:
        practice_id = "physio_default_20min"
    
    # Practice ID mappen
    practice = PracticeId.PHYSIO_DEFAULT_20
    if practice_id == "physio_krebs_nottuln":
        practice = PracticeId.PHYSIO_KREBS_NOTTULN
    elif practice_id == "physio_default_30min":
        practice = PracticeId.PHYSIO_DEFAULT_30
    
    # Intent erkennen
    intent = detect_intent(text)
    
    result = {
        "input_text": text,
        "from_number": from_number,
        "intent": intent,
        "practice_id": practice_id
    }
    
    # Ticket erstellen basierend auf Intent
    if intent == VoiceIntent.BOOKING:
        ticket = auto_book_from_voice(
            practice_id=practice,
            patient_name="Test Patient",
            patient_phone=from_number,
            for_date=date.today(),
        )
        
        if isinstance(ticket, TicketModel) and ticket.slot:
            result.update({
                "status": "booked",
                "ticket_id": ticket.ticket_id,
                "slot": {
                    "start": ticket.slot.start_time.isoformat(),
                    "end": ticket.slot.end_time.isoformat(),
                },
                "message": f"Termin gebucht für {ticket.slot.start_time.strftime('%d.%m.%Y um %H:%M')}"
            })
        else:
            # Kein Slot verfügbar → Callback
            ticket = create_callback_ticket(
                from_number=from_number,
                reason="Kein Slot verfügbar – Rückruf notwendig",
            )
            result.update({
                "status": "callback_created",
                "ticket_id": ticket.ticket_id,
                "message": "Kein Slot verfügbar – Rückruf erstellt"
            })
    
    elif intent == VoiceIntent.CALLBACK:
        ticket = create_callback_ticket(
            from_number=from_number,
            reason=text,
        )
        result.update({
            "status": "callback_created",
            "ticket_id": ticket.ticket_id,
            "message": "Rückruf-Ticket erstellt"
        })
    
    else:
        # Unbekannter Intent → Callback
        ticket = create_callback_ticket(
            from_number=from_number,
            reason=text,
        )
        result.update({
            "status": "callback_created",
            "ticket_id": ticket.ticket_id,
            "message": "Unbekannter Intent – Rückruf erstellt"
        })
    
    return result

