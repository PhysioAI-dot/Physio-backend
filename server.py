from fastapi import FastAPI, Request, WebSocket
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

@app.post("/voice")
async def voice(request: Request):
    """
    Hauptroute für eingehende Twilio-Anrufe.
    Startet den MediaStream und gibt eine kurze Sprachansage aus.
    """

    twiml = f"""
    <?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Start>
            <Stream url="wss://{request.url.hostname}/media-stream" />
        </Start>
        <Say voice="alice">Bitte warten Sie, Bella verbindet sich jetzt.</Say>
    </Response>
    """

    return Response(content=twiml.strip(), media_type="application/xml")

import os
import asyncio
import base64
from openai import AsyncOpenAI

# Hol API-Key aus Render Environment
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def start_realtime_session():
    """
    Baut eine Realtime-Session zu OpenAI auf.
    Noch ohne Audio-Streaming – kommt in Schritt 3.
    """
    try:
        session = await client.realtime.sessions.create(
            model="gpt-4o-realtime-preview",  # oder gpt-5o-realtime wenn verfügbar
            modalities=["audio", "text"],
        )
        print("🔌 Realtime Session gestartet:", session.id)
        return session
    except Exception as e:
        print("⚠️ Fehler bei Realtime:", e)
        return None
# WICHTIG: fehlender Import

@app.websocket("/media-stream")
async def media_stream(websocket: WebSocket):
    await websocket.accept()

    print("🔌 Twilio Medienstream verbunden")

    # Realtime Session starten
    session = await start_realtime_session()

    if session is None:
        await websocket.close()
        print("❌ Realtime Session konnte nicht gestartet werden")
        return

    try:
        while True:
            msg = await websocket.receive_json()

            # Wenn Twilio Audio schickt
            if msg.get("event") == "media":
                audio_b64 = msg["media"]["payload"]
                audio_bytes = base64.b64decode(audio_b64)

                # Audio an OpenAI senden
                await client.realtime.sessions.send_audio(
                    session=session.id,
                    audio=audio_bytes
                )

            # Antworten von OpenAI abrufen
            async for event in client.realtime.sessions.receive(session=session.id):
                if event.type == "response.audio.delta":
                    audio_chunk = event.delta

                    # Audio zurück an Twilio
                    audio_base64 = base64.b64encode(audio_chunk).decode()
                    await websocket.send_json({
                        "event": "media",
                        "media": {
                            "payload": audio_base64
                        }
                    })

    except Exception as e:
        print("⚠️ Fehler im MediaStream:", e)

    finally:
        await websocket.close()
        print("🔌 Twilio Medienstream beendet")
