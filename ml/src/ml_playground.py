from datetime import datetime
from bot.models.word import Word
from bot.models.checker import Checker


def main():
    word = Word(
        word_id=1,
        user_id=1,
        text="house",
        translation="дом",
        base_difficulty=0.4,
        personal_difficulty=0.5,
        difficulty=0.45,
        stability=3.0,
        repeat_count=0,
        ml_score=0.5,
    )

    print("== Стартовое состояние ==")
    print(
        "difficulty:", word.difficulty,
        "personal_difficulty:", word.personal_difficulty,
        "stability:", word.stability,
        "repeat_count:", word.repeat_count,
        "next_repeat:", word.next_repeat,
        "ml_score:", word.ml_score,
    )

    # Первый рейтинг: пользователь говорит, что знает хорошо (3 = Good)
    checker = Checker(user=None, word=word, answer=word.translation)
    checker.update_with_rating(3)
    print("\n== После рейтинга 3 (Good) ==")
    print("feedback:", checker.feedback())
    print(
        "difficulty:", word.difficulty,
        "personal_difficulty:", word.personal_difficulty,
        "stability:", word.stability,
        "repeat_count:", word.repeat_count,
        "next_repeat:", word.next_repeat,
        "ml_score:", word.ml_score,
    )

    # Второй рейтинг: пользователь говорит, что слово тяжёлое (1 = Again)
    checker = Checker(user=None, word=word, answer=word.translation)
    checker.update_with_rating(1)
    print("\n== После рейтинга 1 (Again) ==")
    print("feedback:", checker.feedback())
    print(
        "difficulty:", word.difficulty,
        "personal_difficulty:", word.personal_difficulty,
        "stability:", word.stability,
        "repeat_count:", word.repeat_count,
        "next_repeat:", word.next_repeat,
        "ml_score:", word.ml_score,
    )


if __name__ == "__main__":
    main()
