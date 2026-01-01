"""
Twilio Webhook Handler für Voice-Anrufe
"""
from fastapi import Request, HTTPException
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.request_validator import RequestValidator
import os
import logging
from datetime import date

from schemas import PracticeId, TicketModel
from booking.booking_flow import auto_book_from_voice
from intents.voice_intent import detect_intent, VoiceIntent
from tickets.tickets import create_callback_ticket

# Logger für Twilio-Agent
logger = logging.getLogger("twilio-agent")


async def handle_twilio_webhook(request: Request):
    """
    Twilio Webhook Handler für eingehende Anrufe
    
    Twilio sendet Form-Data mit:
    - From: Anrufer-Nummer
    - CallSid: Eindeutige Call-ID
    - CallStatus: Status des Anrufs
    - SpeechResult: Transkribierter Text (wenn Speech Recognition aktiv)
    """
    try:
        # ============================================================
        # FENSTER 1: ANRUFER-IDENTIFIKATION
        # ============================================================
        form_data = await request.form()
        from_number = form_data.get("From", "Unbekannt")
        call_sid = form_data.get("CallSid", "")
        call_status = form_data.get("CallStatus", "")
        
        print("\n" + "="*60)
        print("--- EINGEHENDER ANRUF ---")
        print(f"Anrufer-Nummer: {from_number}")
        print(f"Call-SID: {call_sid}")
        print(f"Call-Status: {call_status}")
        print("="*60)
        logger.info(f"Eingehender Anruf von {from_number} (CallSid: {call_sid}, Status: {call_status})")
        
        # TwiML Response erstellen
        response = VoiceResponse()
        
        # Wenn SpeechResult vorhanden (Twilio Speech Recognition)
        speech_result = form_data.get("SpeechResult", "")
        
        if speech_result:
            # ============================================================
            # FENSTER 2: USER-SPRACHE (STT - Speech to Text)
            # ============================================================
            print("\n" + "-"*60)
            print("--- USER-SPRACHE ERKANNT (STT) ---")
            print(f"Gesprochener Text: '{speech_result}'")
            print("-"*60)
            logger.info(f"User-Sprache erkannt: '{speech_result}'")
            
            # ============================================================
            # FENSTER 3: INTENT-ERKENNUNG
            # ============================================================
            intent = detect_intent(speech_result)
            print(f"Erkanntes Intent: {intent.value}")
            logger.info(f"Intent erkannt: {intent.value}")
            
            # Ticket erstellen basierend auf Intent
            if intent == VoiceIntent.BOOKING:
                # ============================================================
                # FENSTER 4: TERMINBUCHUNG
                # ============================================================
                print("\n" + "-"*60)
                print("--- TERMINBUCHUNG WIRD VERARBEITET ---")
                print(f"Praxis-ID: {PracticeId.PHYSIO_DEFAULT_20.value}")
                print(f"Patient: Unbekannt (Voice)")
                print(f"Telefon: {from_number}")
                print(f"Datum: {date.today()}")
                print("-"*60)
                logger.info(f"Starte Terminbuchung für {from_number}")
                
                ticket = auto_book_from_voice(
                    practice_id=PracticeId.PHYSIO_DEFAULT_20,
                    patient_name="Unbekannt (Voice)",
                    patient_phone=from_number,
                    for_date=date.today(),
                )
                
                if isinstance(ticket, TicketModel) and ticket.slot:
                    # Buchung erfolgreich
                    slot_time = ticket.slot.start_time.strftime('%d.%m.%Y um %H:%M')
                    response_text = f"Vielen Dank! Ihr Termin wurde für {slot_time} gebucht."
                    
                    print(f"\n[ERFOLG] Termin gebucht!")
                    print(f"  - Ticket-ID: {ticket.ticket_id}")
                    print(f"  - Slot-Zeit: {slot_time}")
                    print(f"  - Status: {ticket.status.value}")
                    print(f"\nAgent-Antwort: '{response_text}'")
                    logger.info(f"Termin erfolgreich gebucht - Ticket-ID: {ticket.ticket_id}, Slot: {slot_time}")
                    
                    response.say(response_text, language="de-DE")
                else:
                    # Kein Slot verfügbar → Callback
                    response_text = "Leider sind aktuell keine Termine verfügbar. Wir rufen Sie gerne zurück."
                    
                    print(f"\n[KEIN SLOT] Fallback zu Callback")
                    print(f"  - Ticket-ID: {ticket.ticket_id if hasattr(ticket, 'ticket_id') else 'N/A'}")
                    print(f"\nAgent-Antwort: '{response_text}'")
                    logger.warning(f"Kein Slot verfügbar - Callback erstellt für {from_number}")
                    
                    response.say(response_text, language="de-DE")
            
            elif intent == VoiceIntent.CALLBACK:
                # ============================================================
                # FENSTER 5: CALLBACK-ERSTELLUNG
                # ============================================================
                print("\n" + "-"*60)
                print("--- CALLBACK-TICKET WIRD ERSTELLT ---")
                print(f"Grund: '{speech_result}'")
                print("-"*60)
                logger.info(f"Callback-Ticket wird erstellt für {from_number}")
                
                ticket = create_callback_ticket(
                    from_number=from_number,
                    reason=speech_result,
                )
                
                response_text = "Vielen Dank für Ihren Anruf. Wir rufen Sie gerne zurück."
                print(f"Ticket-ID: {ticket.ticket_id}")
                print(f"Agent-Antwort: '{response_text}'")
                logger.info(f"Callback-Ticket erstellt - Ticket-ID: {ticket.ticket_id}")
                
                response.say(response_text, language="de-DE")
            
            else:
                # Unbekannter Intent → Callback
                print("\n" + "-"*60)
                print("--- UNBEKANNTES INTENT → CALLBACK ---")
                print(f"Intent: {intent.value}")
                print(f"Text: '{speech_result}'")
                print("-"*60)
                logger.warning(f"Unbekanntes Intent ({intent.value}) - Erstelle Callback für {from_number}")
                
                ticket = create_callback_ticket(
                    from_number=from_number,
                    reason=speech_result,
                )
                
                response_text = "Vielen Dank für Ihren Anruf. Wir melden uns bei Ihnen."
                print(f"Ticket-ID: {ticket.ticket_id}")
                print(f"Agent-Antwort: '{response_text}'")
                logger.info(f"Callback-Ticket erstellt (unbekanntes Intent) - Ticket-ID: {ticket.ticket_id}")
                
                response.say(response_text, language="de-DE")
        
            # ============================================================
            # FENSTER 6: ERSTE BEGRÜSSUNG (Kein SpeechResult)
            # ============================================================
            print("\n" + "-"*60)
            print("--- ERSTE BEGRÜSSUNG ---")
            print("Kein SpeechResult vorhanden - Starte Gather")
            print("-"*60)
            logger.info(f"Erste Begrüßung für {from_number} - Starte Speech Recognition")
            
            # Erste Begrüßung + Speech Recognition aktivieren
            greeting_text = "Guten Tag! Sie erreichen die Praxis. Wie kann ich Ihnen helfen?"
            
            print(f"Agent-Begrüßung: '{greeting_text}'")
            logger.debug(f"Begrüßungstext vorbereitet: '{greeting_text}'")
            
            gather = Gather(
                input="speech",
                language="de-DE",
                action="/voice/twilio-webhook",
                method="POST",
                speech_timeout="auto",
                timeout=10
            )
            gather.say(greeting_text, language="de-DE")
            response.append(gather)
            
            # Fallback wenn keine Eingabe
            fallback_text = "Wir haben Sie nicht verstanden. Bitte rufen Sie erneut an oder hinterlassen Sie eine Nachricht."
            response.say(fallback_text, language="de-DE")
            
            print(f"Fallback-Text: '{fallback_text}'")
            logger.debug("Gather mit Fallback konfiguriert")
        
        # ============================================================
        # FENSTER 7: TWIML-ANTWORT
        # ============================================================
        twiml_content = str(response)
        print("\n" + "-"*60)
        print("--- TWIML-ANTWORT GENERIERT ---")
        print(f"TwiML-Länge: {len(twiml_content)} Zeichen")
        print(f"Media-Type: application/xml")
        print("-"*60)
        logger.debug(f"TwiML-Response generiert ({len(twiml_content)} Zeichen)")
        
        return Response(content=twiml_content, media_type="application/xml")
    
    except Exception as e:
        # ============================================================
        # FEHLERBEHANDLUNG
        # ============================================================
        error_msg = str(e)
        print("\n" + "!"*60)
        print("!!! FEHLER IM WEBHOOK !!!")
        print(f"Fehler: {error_msg}")
        print("!"*60)
        logger.error(f"Fehler im Twilio-Webhook: {error_msg}", exc_info=True)
        
        # Fehler-TwiML zurückgeben
        error_response = VoiceResponse()
        error_response.say("Es ist ein Systemfehler aufgetreten. Bitte versuchen Sie es später erneut.", language="de-DE")
        return Response(content=str(error_response), media_type="application/xml")


async def handle_twilio_status(request: Request):
    """
    Twilio Status Callback für Call-Events
    """
    form_data = await request.form()
    call_sid = form_data.get("CallSid", "")
    call_status = form_data.get("CallStatus", "")
    from_number = form_data.get("From", "")
    
    print("\n" + "-"*60)
    print("--- CALL-STATUS UPDATE ---")
    print(f"Call-SID: {call_sid}")
    print(f"Status: {call_status}")
    print(f"Von: {from_number}")
    print("-"*60)
    logger.info(f"Call-Status Update - CallSid: {call_sid}, Status: {call_status}, From: {from_number}")
    
    # Hier könntest du Call-Status in DB speichern
    # z.B. für Dashboard Live-Anzeige
    
    return {"status": "ok", "call_sid": call_sid, "call_status": call_status}

