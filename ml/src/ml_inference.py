import os
import numpy as np
import joblib

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")

_interval_model = joblib.load(os.path.join(MODELS_DIR, "interval_model.joblib"))
_score_model = joblib.load(os.path.join(MODELS_DIR, "ml_score_model.joblib"))

FEATURE_COLS = [
    "base_difficulty",
    "personal_difficulty",
    "difficulty",
    "repeat_count",
    "stability",
    "user_rating",
]

def predict_interval_and_score(features: dict) -> tuple[float, float]:
    """
    features: словарь с ключами из FEATURE_COLS
    возвращает (interval_days, ml_score)
    """
    x = np.array([[features[col] for col in FEATURE_COLS]], dtype=float)
    interval = float(_interval_model.predict(x)[0])
    score = float(_score_model.predict(x)[0])
    return interval, score