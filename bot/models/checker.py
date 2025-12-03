class Checker:
    def __init__(self, user, word, answer: str):
        self.user = user
        self.word = word
        self.answer = answer.strip().lower()
        self.ml_result = {}

    def check(self) -> bool:
        return self.word.check_translation(self.answer)

    def feedback(self) -> dict:
        return {
            "correct": self.check(),
            "next_repeat_days": self.ml_result.get("next_repeat_days"),
        }

    def evaluate_with_ml(self, ml_model):
        self.ml_result = ml_model.process(self.word, self.answer)
