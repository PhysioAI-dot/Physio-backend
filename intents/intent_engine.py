import re

class IntentEngine:
    def detect_intent(self, text: str) -> str:
        text = text.lower()

        if re.search(r"\btermin\b|\btermin\b|\bbuchen\b|\bvereinbaren\b", text):
            return "termin"

        if re.search(r"\brückfrage\b|\bfrage\b|\bklären\b", text):
            return "rueckfrage"

        return "other"
