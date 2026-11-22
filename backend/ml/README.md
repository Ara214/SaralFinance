# Bundled risk classifier

The supplied artifact is a fitted scikit-learn character TF-IDF and Linear SVM pipeline. The app loads it at startup and predicts Low, Medium, or High for each message. The original training script and metrics are included. Inference uses scikit-learn 1.6.1, the version embedded in the artifact.

Run `python -m evaluation.evaluate_risk --hybrid` from the app root to evaluate the deployed decision rule. The app returns the higher of the classifier and rules tiers. The API's numeric risk score comes from the rules.

Load joblib files only from sources you trust. To reproduce training in a separate checkout, install pandas in the backend environment and run `python backend/ml/train_model_v1.py`. This command overwrites the model and training metrics.
