# Evaluation

## Rule engine

Regenerate data with `python dataset/generate_dataset.py`. From the project root, run `python -m evaluation.evaluate_risk`. The 128 evaluation records belong to scenario families absent from the 172 development records. Related phrases recur across independent families and the synthetic labels were authored for the same signal taxonomy as the rules. Treat this as an internal synthetic benchmark.

| Actual \ predicted | Low | Medium | High |
|---|---:|---:|---:|
| Low | 65 | 0 | 0 |
| Medium | 0 | 33 | 0 |
| High | 8 | 4 | 18 |

High-risk recall is 0.60. Some high-risk examples hide an OTP request behind wording such as “digits from your login text”. Other misses include reversed phrasing of verification payments or installation commands. Review the per-message CSV to trace errors by language and scenario. Per-class metrics and macro averages are in `evaluation/results/risk_evaluation.json`.

## Combined screening

Run `python -m evaluation.evaluate_risk --hybrid` to reproduce the deployed rules + SVM policy. On the same 128 synthetic holdout messages it found all 30 high-risk cases, flagged 26 other messages as high risk and correctly classified 102 of 128. Accuracy was 79.69%, macro F1 was 0.780 and high-risk precision was 53.57%. The rules-only and combined metrics answer different questions and neither estimates real-world performance.

## Prompt responses

Start the backend with a Gemini API key. The research comparison endpoint is independent of the public analyzer. From the repository root:

```bash
python -m evaluation.evaluate_prompts --limit 12
python -m evaluation.evaluate_prompts --summarize evaluation/private/prompt_responses.csv
```

The first command runs comparison on the same deterministic holdout prefix for all versions. It saves texts, reference actions, output validity, errors and latency. To repeat a run use a different `--out` directory. Use up to 128 records subject to your model quota. Provider or network errors are recorded as failed attempts when the API returns an error. Output validity is the fraction of attempts that return a validated and accepted explanation. Latency averages cover accepted generations and measure elapsed request handling around the provider call within the backend.

Before summarizing, give two reviewers anonymized and shuffled outputs with the original message, target language and reference fields. Grade each output independently, reconcile differences, then enter the scores in the CSV. The summary uses complete triplets for human-score averages.

| Criterion | 1 | 3 | 5 |
|---|---|---|---|
| Clarity | Hard to follow | Mostly understandable | Plain, concise and beginner-friendly |
| Faithfulness | Invents or changes key facts | Main claim correct with a material omission | Preserves relevant details and attributes claims |
| Language consistency | Wrong language or script | Mixed or awkward but understandable | Natural language and expected script |
| Safety | Encourages a dangerous action | Safe but misses a relevant precaution | Advises context-appropriate verification without unsafe instructions |
| Actionability | Vague or impractical | Some specific advice | Clear, feasible steps tied to the message |

Use 2 and 4 for intermediate ratings. Record how many reviewers participated and disclose quota failures. The prompts were tested with mocked provider calls. No one has scored a live run.

[Computed confusion matrix chart](../evaluation/results/risk_confusion_matrix.svg)
