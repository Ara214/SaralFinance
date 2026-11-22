"""Combine the bundled text classifier with the original explainable rules."""
from functools import lru_cache
from pathlib import Path

import joblib

from .risk_detector import WARNINGS, assess

MODEL_PATH = Path(__file__).resolve().parents[1] / "ml" / "models" / "risk_classifier.joblib"
LEVELS = {"Low": 0, "Medium": 1, "High": 2}
LANGUAGES = ("english", "hindi", "hinglish")
MODEL_SIGNAL = (
    "The message wording resembles examples that require extra caution.",
    "इस संदेश की भाषा ऐसे उदाहरणों से मिलती है जिनमें अतिरिक्त सावधानी चाहिए।",
    "Message ki wording aise examples se milti hai jinmein extra caution chahiye.",
)


@lru_cache(maxsize=1)
def load_classifier():
    # Load only the bundled project artifact. Joblib can execute code while loading.
    model = joblib.load(MODEL_PATH)
    if set(model.classes_) != set(LEVELS):
        raise ValueError("Unexpected risk labels in the bundled model.")
    return model


def predict_risk(message):
    return str(load_classifier().predict([message])[0])


def combine_risk(rules, prediction, language):
    rules_level = rules["risk_level"]
    result = {**rules, "rules_risk_level": rules_level, "model_risk_level": prediction}
    if LEVELS[prediction] > LEVELS[rules_level]:
        locale = LANGUAGES.index(language)
        result["risk_level"] = prediction
        result["risk_reasons"] = [*rules["risk_reasons"], MODEL_SIGNAL[locale]]
        result["risk_warning"] = WARNINGS[locale]
    return result


def assess_message(message, language):
    return combine_risk(assess(message, language), predict_risk(message), language)
