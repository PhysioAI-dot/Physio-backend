from datetime import datetime, time, timedelta, date
from typing import List, Dict

from schemas import SlotModel, SlotType



SLOT_DURATION_MINUTES = 20


# -------------------------------------------------
# Wochenplan – Physio Krebs Nottuln (Premium)
# -------------------------------------------------

WEEKLY_PLAN: Dict[int, Dict] = {
    # Montag
    0: {
        "open": time(8, 30),
        "close": time(18, 30),
        "admin": [
            (time(8, 0), time(8, 30)),
            (time(10, 30), time(11, 0)),
            (time(13, 0), time(14, 0)),
            (time(16, 0), time(16, 30)),
        ],
        "house_visit": [],
    },

    # Dienstag
    1: {
        "open": time(8, 30),
        "close": time(19, 0),
        "admin": [
            (time(16, 0), time(16, 20)),
        ],
        "house_visit": [
            (time(8, 30), time(14, 0)),
        ],
    },

    # Mittwoch
    2: {
        "open": time(6, 30),
        "close": time(18, 0),
        "admin": [
            (time(6, 30), time(7, 0)),
            (time(9, 0), time(9, 30)),
            (time(11, 30), time(12, 0)),
            (time(14, 0), time(14, 30)),
        ],
        "house_visit": [
            (time(15, 0), time(18, 0)),  # Option A: keine Slots
        ],
    },

    # Donnerstag
    3: {
        "open": time(8, 0),
        "close": time(19, 0),
        "admin": [
            (time(8, 0), time(8, 30)),
            (time(10, 30), time(11, 0)),
            (time(13, 0), time(14, 0)),
            (time(16, 0), time(16, 30)),
            (time(18, 30), time(19, 0)),
        ],
        "house_visit": [],
    },

    # Freitag
    4: {
        "open": time(14, 0),
        "close": time(18, 30),
        "admin": [
            (time(14, 0), time(14, 30)),
            (time(16, 30), time(17, 0)),
        ],
        "house_visit": [],
    },

    # Samstag
    5: {
        "open": time(12, 0),
        "close": time(16, 0),
        "admin": [],
        "house_visit": [],
    },
}


# -------------------------------------------------
# Hilfsfunktionen
# -------------------------------------------------

def _is_in_ranges(check_time: datetime, ranges, for_date: date) -> bool:
    for start, end in ranges:
        if datetime.combine(for_date, start) <= check_time < datetime.combine(for_date, end):
            return True
    return False


# -------------------------------------------------
# Slot-Generator – Premium Krebs Praxis
# -------------------------------------------------

def generate_krebs_slots(for_date: date) -> List[SlotModel]:
    weekday = for_date.weekday()

    # Sonntag oder nicht definiert → keine Slots
    if weekday not in WEEKLY_PLAN:
        return []

    day = WEEKLY_PLAN[weekday]

    slots: List[SlotModel] = []

    current_start = datetime.combine(for_date, day["open"])
    end_of_day = datetime.combine(for_date, day["close"])

    while current_start + timedelta(minutes=SLOT_DURATION_MINUTES) <= end_of_day:
        current_end = current_start + timedelta(minutes=SLOT_DURATION_MINUTES)

        # Hausbesuch → blockiert
        if _is_in_ranges(current_start, day["house_visit"], for_date):
            slots.append(
                SlotModel(
                    start_time=current_start,
                    end_time=current_end,
                    duration_minutes=SLOT_DURATION_MINUTES,
                    slot_type=SlotType.HOUSE_VISIT,
                    is_bookable=False,
                )
            )

        # Verwaltung → blockiert
        elif _is_in_ranges(current_start, day["admin"], for_date):
            slots.append(
                SlotModel(
                    start_time=current_start,
                    end_time=current_end,
                    duration_minutes=SLOT_DURATION_MINUTES,
                    slot_type=SlotType.ADMIN,
                    is_bookable=False,
                )
            )

        # Behandlung → buchbar
        else:
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
