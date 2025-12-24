import os
import pandas as pd
import joblib

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")

FEATURE_COLS = [
    "base_difficulty",
    "personal_difficulty",
    "difficulty",
    "repeat_count",
    "stability",
    "user_rating",
]

_interval_model = None
_score_model = None


def _load_models():
    global _interval_model, _score_model

    try:
        interval_path = os.path.join(MODELS_DIR, "interval_model.joblib")
        score_path = os.path.join(MODELS_DIR, "ml_score_model.joblib")

        _interval_model = joblib.load(interval_path)
        _score_model = joblib.load(score_path)

        print("ML модели успешно загружены")

    except Exception as e:
        _interval_model = None
        _score_model = None
        print("ML модели НЕ загружены, используется fallback")
        print(f"Причина: {e}")


_load_models()


def predict_interval_and_score(features: dict) -> tuple[float, float]:
    """
    Возвращает (interval_days, ml_score)

    Если ML недоступен → fallback значения
    """
    if _interval_model is None or _score_model is None:
        difficulty = features.get("difficulty", 0.5)
        repeat_count = features.get("repeat_count", 1)

        interval_days = max(1.0, 1 + repeat_count * (1 - difficulty))
        ml_score = max(0.1, min(1.0, 1 - difficulty))

        return float(interval_days), float(ml_score)

    x = pd.DataFrame([features], columns=FEATURE_COLS)

    interval = float(_interval_model.predict(x)[0])
    score = float(_score_model.predict(x)[0])

    return interval, score
