"""
Twilio Webhook Handler für Voice-Anrufe
"""
from fastapi import Request, HTTPException
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.request_validator import RequestValidator
import os
from datetime import date

from schemas import PracticeId, TicketModel
from booking.booking_flow import auto_book_from_voice
from intents.voice_intent import detect_intent, VoiceIntent
from tickets.tickets import create_callback_ticket


async def handle_twilio_webhook(request: Request):
    """
    Twilio Webhook Handler für eingehende Anrufe
    
    Twilio sendet Form-Data mit:
    - From: Anrufer-Nummer
    - CallSid: Eindeutige Call-ID
    - CallStatus: Status des Anrufs
    - SpeechResult: Transkribierter Text (wenn Speech Recognition aktiv)
    """
    
    # Form-Data von Twilio lesen
    form_data = await request.form()
    from_number = form_data.get("From", "")
    call_sid = form_data.get("CallSid", "")
    call_status = form_data.get("CallStatus", "")
    
    # TwiML Response erstellen
    response = VoiceResponse()
    
    # Wenn SpeechResult vorhanden (Twilio Speech Recognition)
    speech_result = form_data.get("SpeechResult", "")
    
    if speech_result:
        # Intent erkennen
        intent = detect_intent(speech_result)
        
        # Ticket erstellen basierend auf Intent
        if intent == VoiceIntent.BOOKING:
            ticket = auto_book_from_voice(
                practice_id=PracticeId.PHYSIO_DEFAULT_20,
                patient_name="Unbekannt (Voice)",
                patient_phone=from_number,
                for_date=date.today(),
            )
            
            if isinstance(ticket, TicketModel) and ticket.slot:
                # Buchung erfolgreich
                response.say(
                    f"Vielen Dank! Ihr Termin wurde für {ticket.slot.start_time.strftime('%d.%m.%Y um %H:%M')} gebucht.",
                    language="de-DE"
                )
            else:
                # Kein Slot verfügbar → Callback
                response.say(
                    "Leider sind aktuell keine Termine verfügbar. Wir rufen Sie gerne zurück.",
                    language="de-DE"
                )
        
        elif intent == VoiceIntent.CALLBACK:
            ticket = create_callback_ticket(
                from_number=from_number,
                reason=speech_result,
            )
            response.say(
                "Vielen Dank für Ihren Anruf. Wir rufen Sie gerne zurück.",
                language="de-DE"
            )
        
        else:
            # Unbekannter Intent → Callback
            ticket = create_callback_ticket(
                from_number=from_number,
                reason=speech_result,
            )
            response.say(
                "Vielen Dank für Ihren Anruf. Wir melden uns bei Ihnen.",
                language="de-DE"
            )
    
    else:
        # Erste Begrüßung + Speech Recognition aktivieren
        gather = Gather(
            input="speech",
            language="de-DE",
            action="/voice/twilio-webhook",
            method="POST",
            speech_timeout="auto",
            timeout=10
        )
        gather.say(
            "Guten Tag! Sie erreichen die Praxis. Wie kann ich Ihnen helfen?",
            language="de-DE"
        )
        response.append(gather)
        
        # Fallback wenn keine Eingabe
        response.say(
            "Wir haben Sie nicht verstanden. Bitte rufen Sie erneut an oder hinterlassen Sie eine Nachricht.",
            language="de-DE"
        )
    
    # TwiML XML zurückgeben
    return Response(content=str(response), media_type="application/xml")


async def handle_twilio_status(request: Request):
    """
    Twilio Status Callback für Call-Events
    """
    form_data = await request.form()
    call_sid = form_data.get("CallSid", "")
    call_status = form_data.get("CallStatus", "")
    from_number = form_data.get("From", "")
    
    # Hier könntest du Call-Status in DB speichern
    # z.B. für Dashboard Live-Anzeige
    
    return {"status": "ok", "call_sid": call_sid, "call_status": call_status}

