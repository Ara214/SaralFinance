from pathlib import Path
import json
import joblib
import pandas as pd

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.model_selection import GroupKFold, cross_validate
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "dataset" / "synthetic_messages.csv"
OUTPUT_DIR = Path(__file__).resolve().parent / "models"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA_PATH)

required = [
    "message_text",
    "ground_truth_risk",
    "scenario",
    "split",
]
assert all(col in df.columns for col in required)
assert not df[required].isna().any().any()

dev = df[df["split"] == "development"].copy()
test = df[df["split"] == "evaluation"].copy()

assert len(dev) > 0 and len(test) > 0
assert set(dev["scenario"]).isdisjoint(set(test["scenario"]))

X_train = dev["message_text"].astype(str)
y_train = dev["ground_truth_risk"]
groups = dev["scenario"]

X_test = test["message_text"].astype(str)
y_test = test["ground_truth_risk"]

models = {
    "Logistic Regression": LogisticRegression(
        max_iter=2000,
        class_weight="balanced",
        random_state=42,
    ),
    "Linear SVM": LinearSVC(
        class_weight="balanced",
        random_state=42,
    ),
}

cv = GroupKFold(n_splits=3)
results = {}

for name, classifier in models.items():
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            analyzer="char",
            ngram_range=(2, 5),
            sublinear_tf=True,
        )),
        ("classifier", classifier),
    ])

    scores = cross_validate(
        pipeline,
        X_train,
        y_train,
        groups=groups,
        cv=cv,
        scoring={
            "accuracy": "accuracy",
            "f1_macro": "f1_macro",
        },
        error_score="raise",
    )

    results[name] = scores["test_f1_macro"].mean()

    print(f"\n{name}")
    print("CV Accuracy:", scores["test_accuracy"].mean())
    print("CV Macro F1:", results[name])

best_name = max(results, key=results.get)
print("\nSelected model:", best_name)

best_model = Pipeline([
    ("tfidf", TfidfVectorizer(
        analyzer="char",
        ngram_range=(2, 5),
        sublinear_tf=True,
    )),
    ("classifier", models[best_name]),
])

best_model.fit(X_train, y_train)

predictions = best_model.predict(X_test)

labels = ["Low", "Medium", "High"]

print("\nFinal Test Accuracy:")
print(accuracy_score(y_test, predictions))

print("\nClassification Report:")
print(classification_report(
    y_test,
    predictions,
    labels=labels,
    zero_division=0,
))

cm = confusion_matrix(
    y_test,
    predictions,
    labels=labels,
)

print("\nConfusion Matrix:")
print(cm)

joblib.dump(
    best_model,
    OUTPUT_DIR / "risk_classifier.joblib",
)

report = classification_report(
    y_test,
    predictions,
    labels=labels,
    output_dict=True,
    zero_division=0,
)

with open(OUTPUT_DIR / "metrics.json", "w") as f:
    json.dump({
        "selected_model": best_name,
        "cv_macro_f1": results,
        "test_accuracy": accuracy_score(
            y_test, predictions
        ),
        "classification_report": report,
        "confusion_matrix": cm.tolist(),
        "labels": labels,
    }, f, indent=2)

print("\nModel and metrics saved successfully!")