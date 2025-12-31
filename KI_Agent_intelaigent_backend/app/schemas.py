from enum import Enum
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field
from uuid import uuid4

# -------------------------------------------------
# Praxis-IDs
# -------------------------------------------------
class PracticeId(str, Enum):
    PHYSIO_KREBS_NOTTULN = "physio_krebs_nottuln"
    PHYSIO_DEFAULT_20 = "physio_default_20min"
    PHYSIO_DEFAULT_30 = "physio_default_30min"

# -------------------------------------------------
# Slot-Typen
# -------------------------------------------------
class SlotType(str, Enum):
    TREATMENT = "treatment"
    ADMIN = "admin"
    HOUSE_VISIT = "house_visit"

class SlotModel(BaseModel):
    start_time: datetime
    end_time: datetime
    duration_minutes: int
    slot_type: SlotType
    is_bookable: bool = True

# -------------------------------------------------
# Booking Request
# -------------------------------------------------
class BookingRequest(BaseModel):
    practice_id: PracticeId
    patient_name: str
    patient_phone: Optional[str] = None
    patient_email: Optional[str] = None
    requested_date: date
    requested_time: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

# -------------------------------------------------
# Ticket-System Status
# -------------------------------------------------
class TicketStatus(str, Enum):
    OPEN = "open"
    BOOKED = "booked"
    CALLBACK = "callback"
    CLOSED = "closed"

class TicketModel(BaseModel):
    # Wir machen ticket_id optional oder geben einen Standard, 
    # falls die DB die ID erst später vergibt
    ticket_id: Optional[str] = None 
    practice_id: PracticeId
    booking_request: BookingRequest
    slot: Optional[SlotModel] = None
    status: TicketStatus
    message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

# -------------------------------------------------
# Callback & Voice
# -------------------------------------------------
class CallbackTicket(BaseModel):
    ticket_id: str = Field(default_factory=lambda: str(uuid4()))
    practice_id: PracticeId = PracticeId.PHYSIO_DEFAULT_20
    patient_name: str = "Unbekannt (Voice)"
    patient_phone: Optional[str] = None
    reason: str
    status: TicketStatus = TicketStatus.CALLBACK
    created_at: datetime = Field(default_factory=datetime.utcnow)

class VoicePayload(BaseModel):
    from_number: str
    text: str