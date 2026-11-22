import argparse
import csv
import json
from collections import Counter
from pathlib import Path

from backend.app.risk_detector import assess

ROOT = Path(__file__).resolve().parents[1]
LEVELS = ("Low", "Medium", "High")


def evaluate(rows, assessor=assess):
    matrix = Counter()
    decisions = []
    for row in rows:
        result = assessor(row["message_text"], row["language"])
        actual, predicted = row["ground_truth_risk"], result["risk_level"]
        matrix[actual, predicted] += 1
        decisions.append({"message_id": row["message_id"], "scenario": row["scenario"], "language": row["language"],
                          "expected": actual, "predicted": predicted, "score": result["risk_score"]})
    metrics = {}
    for level in LEVELS:
        true = matrix[level, level]
        support = sum(matrix[level, other] for other in LEVELS)
        positives = sum(matrix[other, level] for other in LEVELS)
        precision = true / positives if positives else 0
        recall = true / support if support else 0
        metrics[level] = {"precision": precision, "recall": recall,
                          "f1": 2 * precision * recall / (precision + recall) if precision + recall else 0,
                          "support": support}
    return ({
        "samples": len(rows), "accuracy": sum(matrix[level, level] for level in LEVELS) / len(rows),
        "classes": metrics, "macro": {key: sum(metric[key] for metric in metrics.values()) / len(LEVELS)
                                       for key in ("precision", "recall", "f1")},
        "labels": list(LEVELS), "confusion_matrix": [[matrix[a, b] for b in LEVELS] for a in LEVELS],
    }, decisions)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", choices=["evaluation", "development", "all"], default="evaluation")
    parser.add_argument("--out", type=Path, default=ROOT / "evaluation" / "results")
    parser.add_argument("--hybrid", action="store_true", help="Use the same combined risk assessment as the analyzer.")
    args = parser.parse_args()
    with (ROOT / "dataset" / "synthetic_messages.csv").open(encoding="utf-8") as handle:
        rows = [row for row in csv.DictReader(handle) if args.split in ("all", row["split"])]
    if args.hybrid:
        from backend.app.risk_model import assess_message
        summary, decisions = evaluate(rows, assess_message)
    else:
        summary, decisions = evaluate(rows)
    prefix = "hybrid" if args.hybrid else "risk"
    summary["split"] = args.split
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / f"{prefix}_{args.split}.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    with (args.out / f"{prefix}_{args.split}.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(decisions[0]))
        writer.writeheader()
        writer.writerows(decisions)
    print(json.dumps(summary, indent=2))
