from collections import Counter

from backend.app.prompts.few_shot import EXAMPLES
from dataset.generate_dataset import CATALOG, build
from evaluation.evaluate_risk import evaluate


def test_dataset_is_reproducible_and_split_by_scenario():
    rows = build()
    assert rows == build()
    assert Counter(row["category"] for row in rows) == {name: count for name, (count, _) in CATALOG.items()}
    dev = {row["scenario"] for row in rows if row["split"] == "development"}
    holdout = [row for row in rows if row["split"] == "evaluation"]
    assert dev.isdisjoint(row["scenario"] for row in holdout)
    assert {message for _, message, _, _ in EXAMPLES}.isdisjoint(row["message_text"] for row in holdout)
    metrics, decisions = evaluate(holdout)
    assert len(decisions) == sum(map(sum, metrics["confusion_matrix"])) == len(holdout)
