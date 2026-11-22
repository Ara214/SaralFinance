"""Capture real outputs for human grading, then summarize completed ratings."""
import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from statistics import mean

import httpx

ROOT = Path(__file__).resolve().parents[1]
CRITERIA = ("clarity", "faithfulness", "language_consistency", "safety", "actionability")
VERSIONS = ("P0", "P1", "P2")


def capture(url, limit, output):
    with (ROOT / "dataset" / "synthetic_messages.csv").open(encoding="utf-8") as handle:
        sample = [row for row in csv.DictReader(handle) if row["split"] == "evaluation"][:limit]
    with httpx.Client(base_url=url, timeout=30) as client:
        health = client.get("/health")
        health.raise_for_status()
        if health.json()["mode"] != "gemini":
            raise SystemExit("Prompt evaluation requires a configured Gemini API key.")
        output.mkdir(parents=True, exist_ok=True)
        fields = ["message_id", "prompt_version", "message_text", "language", "reference_explanation", "expected_action",
                  "what_happened", "what_to_do_next", "analogy", "response_ms", "structured_valid", "error", *CRITERIA]
        with (output / "prompt_responses.csv").open("x", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            for row in sample:
                response = client.post("/api/compare", json={"message": row["message_text"], "language": row["language"]})
                results = response.json()["results"] if response.is_success else []
                by_version = {item["prompt_version"]: item for item in results}
                for version in VERSIONS:
                    result = by_version.get(version, {})
                    valid = result.get("source") == "gemini"
                    writer.writerow({
                        **{name: row[name] for name in fields if name in row},
                        "prompt_version": version, "structured_valid": int(valid),
                        "what_happened": result.get("what_happened"), "analogy": result.get("analogy"),
                        "what_to_do_next": json.dumps(result.get("what_to_do_next"), ensure_ascii=False) if valid else "",
                        "response_ms": result.get("response_ms"),
                        "error": result.get("error", "" if valid else f"HTTP {response.status_code}: {response.json().get('detail', '')}"),
                    })
                handle.flush()


def summarize(source):
    with source.open(encoding="utf-8") as handle:
        data = list(csv.DictReader(handle))
    valid_pairs = Counter(row["message_id"] for row in data if row["structured_valid"] == "1"
                          and all(row[key] in {"1", "2", "3", "4", "5"} for key in CRITERIA))
    outcomes = {}
    for version in VERSIONS:
        rows = [row for row in data if row["prompt_version"] == version]
        if not rows:
            continue
        valid = [row for row in rows if row["structured_valid"] == "1"]
        rated = [row for row in valid if valid_pairs[row["message_id"]] == len(VERSIONS)]
        outcomes[version] = {
            "attempts": len(rows), "valid_outputs": len(valid), "structured_valid_rate": len(valid) / len(rows),
            "mean_response_ms": mean(float(row["response_ms"]) for row in valid) if valid else None,
            "paired_human_ratings": len(rated),
            "mean_human_rating_out_of_5": {key: mean(int(row[key]) for row in rated) for key in CRITERIA} if rated else None,
        }
    source.with_name("prompt_summary.json").write_text(json.dumps(outcomes, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8000")
    parser.add_argument("--limit", type=int, default=12)
    parser.add_argument("--out", type=Path, default=ROOT / "evaluation" / "private")
    parser.add_argument("--summarize", type=Path)
    args = parser.parse_args()
    if args.summarize:
        summarize(args.summarize)
    elif args.limit > 0:
        capture(args.url, args.limit, args.out)
    else:
        parser.error("--limit must be positive")
