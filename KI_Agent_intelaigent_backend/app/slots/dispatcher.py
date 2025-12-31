from datetime import date
from typing import List

from app.schemas import SlotModel, PracticeId

from app.slots.default20 import generate_default20_slots
from app.slots.default30 import generate_default30_slots
from app.slots.physio_krebs_nottuln import generate_krebs_slots




# -------------------------------------------------
# Zentrale Slot-Auswahl
# -------------------------------------------------

def get_slots_for_practice(
    practice_id: PracticeId,
    for_date: date
) -> List[SlotModel]:
    """
    Zentrale Slot-Funktion für das gesamte Backend.
    Entscheidet anhand der Praxis-ID, welche Slot-Logik greift.
    """

    if practice_id == PracticeId.PHYSIO_DEFAULT_20:
        return generate_default20_slots(for_date)

    if practice_id == PracticeId.PHYSIO_DEFAULT_30:
        return generate_default30_slots(for_date)

    if practice_id == PracticeId.PHYSIO_KREBS_NOTTULN:
        return generate_krebs_slots(for_date)

    # Fallback (sollte nie passieren)
    return []
