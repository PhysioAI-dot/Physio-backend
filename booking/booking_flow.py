from datetime import datetime, date
from typing import Union
from uuid import uuid4

from schemas import (
    BookingRequest,
    TicketModel,
    CallbackTicket,
    TicketStatus,
    SlotType,
)
from slots.dispatcher import get_slots_for_practice


# -------------------------------------------------
# Booking Flow – API / Formular / Dashboard
# -------------------------------------------------

def process_booking_request(
    booking_request: BookingRequest,
) -> Union[TicketModel, CallbackTicket]:
    """
    Zentrale Booking-Logik (reiner Decision-Flow):
    - Slots abrufen
    - Hausbesuch prüfen
    - Ticket ODER Callback zurückgeben
    - KEINE Persistenz
    """

    slots = get_slots_for_practice(
        practice_id=booking_request.practice_id,
        for_date=booking_request.requested_date,
    )

    # Kein Slot → Callback
    if not slots:
        return CallbackTicket(
            practice_id=booking_request.practice_id,
            patient_name=booking_request.patient_name,
            patient_phone=booking_request.patient_phone,
            reason="Keine verfügbaren Slots an diesem Tag",
        )

    # Hausbesuch → Callback
    for slot in slots:
        if slot.slot_type == SlotType.HOUSE_VISIT:
            return CallbackTicket(
                practice_id=booking_request.practice_id,
                patient_name=booking_request.patient_name,
                patient_phone=booking_request.patient_phone,
                reason="Hausbesuch – Rückruf erforderlich",
            )

    # Erster buchbarer Slot
    for slot in slots:
        if slot.is_bookable:
            return TicketModel(
                ticket_id=str(uuid4()),
                practice_id=booking_request.practice_id,
                booking_request=booking_request,   # 🔥 ENTSCHEIDEND
                slot=slot,
                status=TicketStatus.BOOKED,
                message="Termin gebucht",
                created_at=datetime.utcnow(),
            )

    # Fallback
    return CallbackTicket(
        practice_id=booking_request.practice_id,
        patient_name=booking_request.patient_name,
        patient_phone=booking_request.patient_phone,
        reason="Kein buchbarer Slot gefunden",
    )


# -------------------------------------------------
# Booking Flow – Voice Shortcut
# -------------------------------------------------

def auto_book_from_voice(
    practice_id,
    patient_name: str,
    patient_phone: str,
    for_date: date,
) -> Union[TicketModel, CallbackTicket]:
    """
    Vereinfachtes Booking für Voice:
    - erster freier Slot
    - sonst Callback
    """

    slots = get_slots_for_practice(
        practice_id=practice_id,
        for_date=for_date,
    )

    if not slots:
        return CallbackTicket(
            practice_id=practice_id,
            patient_name=patient_name,
            patient_phone=patient_phone,
            reason="Kein Slot verfügbar – Rückruf notwendig",
        )

    slot = slots[0]

    return TicketModel(
        ticket_id=str(uuid4()),
        practice_id=practice_id,
        booking_request=BookingRequest(
            practice_id=practice_id,
            patient_name=patient_name,
            patient_phone=patient_phone,
            requested_date=for_date,
        ),
        slot=slot,
        status=TicketStatus.BOOKED,
        message="Termin gebucht (Voice)",
        created_at=datetime.utcnow(),
    )
