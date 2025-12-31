class IntentEngine:
    def detect_intent(self, text: str) -> str:
        text = text.lower()

        if "termin" in text:
            return "booking"
        if "rückruf" in text or "zurückrufen" in text:
            return "callback"
        if "frage" in text or "info" in text:
            return "info"

        return "unknown"
