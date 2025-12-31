from enum import Enum


class VoiceIntent(str, Enum):
    BOOKING = "booking"
    CALLBACK = "callback"
    CANCEL = "cancel"
    UNKNOWN = "unknown"


def detect_intent(text: str) -> VoiceIntent:
    t = text.lower()

    booking_keywords = [
        "termin",
        "termin machen",
        "termin vereinbaren",
        "buchen",
        "vereinbaren",
        "zeit",
        "kommen",
        "dringend",
    ]

    callback_keywords = [
        "rückruf",
        "zurückrufen",
        "anrufen",
        "bitte anrufen",
        "melden",
        "kontakt",
    ]

    cancel_keywords = [
        "absagen",
        "stornieren",
        "verschieben",
        "doch nicht",
        "nicht kommen",
    ]

    if any(k in t for k in booking_keywords):
        return VoiceIntent.BOOKING

    if any(k in t for k in cancel_keywords):
        return VoiceIntent.CANCEL

    if any(k in t for k in callback_keywords):
        return VoiceIntent.CALLBACK

    return VoiceIntent.UNKNOWN
