from datetime import datetime, time, timedelta, date
from typing import List

from app.schemas import SlotModel, SlotType



OPEN_TIME = time(8, 0)
CLOSE_TIME = time(18, 0)
SLOT_DURATION_MINUTES = 20


def generate_default20_slots(for_date: date) -> List[SlotModel]:
    """
    Standardpraxis:
    - Montag–Freitag
    - 08:00–18:00
    - 20-Minuten-Slots
    """

    # Wochenende = keine Slots
    if for_date.weekday() >= 5:
        return []

    slots: List[SlotModel] = []

    current_start = datetime.combine(for_date, OPEN_TIME)
    end_of_day = datetime.combine(for_date, CLOSE_TIME)

    while current_start + timedelta(minutes=SLOT_DURATION_MINUTES) <= end_of_day:
        current_end = current_start + timedelta(minutes=SLOT_DURATION_MINUTES)

        slots.append(
            SlotModel(
                start_time=current_start,
                end_time=current_end,
                duration_minutes=SLOT_DURATION_MINUTES,
                slot_type=SlotType.TREATMENT,
                is_bookable=True,
            )
        )

        current_start = current_end

    return slots
