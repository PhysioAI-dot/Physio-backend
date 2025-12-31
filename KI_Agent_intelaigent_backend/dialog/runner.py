import sys
from pathlib import Path
import json

# ---------------------------------------
# Projektpfad sauber setzen
# ---------------------------------------
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from dialog.engine import DialogEngine
from intents.intent_engine import IntentEngine


def normalize_intent(raw_intent: str | None) -> str | None:
    """
    FINAL:
    - KEINE Text-Heuristiken
    - KEINE Slot-Interpretation
    - Intents kommen ausschließlich aus der IntentEngine
    """
    return raw_intent


# ---------------------------------------
# States laden
# ---------------------------------------
with open(BASE_DIR / "dialog" / "states.json", encoding="utf-8") as f:
    states = json.load(f)

dialog_engine = DialogEngine(states)
intent_engine = IntentEngine()

# ---------------------------------------
# Start
# ---------------------------------------
print("AGENT:", dialog_engine.step())

while True:
    user_input = input("USER: ").strip()
    if not user_input:
        continue

    raw_intent = intent_engine.detect_intent(user_input)
    intent = normalize_intent(raw_intent)

    response = dialog_engine.step(
        user_input=user_input,
        intent=intent
    )

    print("AGENT:", response)
