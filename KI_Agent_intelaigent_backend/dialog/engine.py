class DialogEngine:
    def __init__(self, states: dict):
        self.states = states
        self.current_state = "START"
        self.context = {}

    def get_prompt(self) -> str:
        return self.states[self.current_state].get("prompt", "")

    def step(self, user_input: str | None = None, intent: str | None = None) -> str:
        state = self.states[self.current_state]

        # 1. Daten speichern (Slot-Filling)
        if user_input and "save" in state:
            self.context[state["save"]] = user_input

        # 2. Intent-gesteuerter Übergang (NUR wo explizit definiert)
        if intent and "on_intent" in state:
            self.current_state = state["on_intent"].get(intent, self.current_state)

        # 3. Standard-Übergang
        elif "next" in state:
            self.current_state = state["next"]

        return self.get_prompt()
