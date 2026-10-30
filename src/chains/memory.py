class ConversationMemory:
    def __init__(self, max_turns: int = 5):
        self.history = []
        self.max_turns = max_turns

    def add_turn(self, role: str, content: str):
        self.history.append((role, content))
        if len(self.history) > self.max_turns * 2:
            self.history = self.history[-self.max_turns * 2:]

    def get_formatted_history(self) -> str:
        return "\n".join([f"{r.capitalize()}: {t}" for r, t in self.history])

    def reset(self):
        self.history = []
