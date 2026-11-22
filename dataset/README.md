# Synthetic financial messages

`synthetic_messages.csv` contains 300 synthetic messages in English, Hindi and Hinglish. The eight categories contain 60 bank alerts, 50 UPI alerts, 40 KYC alerts, 40 credential messages, 30 loans, 30 insurance notices, 30 reward and phishing messages and 20 miscellaneous alerts.

Run `python dataset/generate_dataset.py` from the project root to regenerate. A fixed seed controls amounts and ordering. The generator uses manually authored scenario families with three language realizations each. Whole families are allocated to development or evaluation. Variation within a family comes from amount and deadline slots. Labels and references are scenario-level annotations and remain synthetic.

The dataset includes low, medium and high risk messages, warnings against sharing credentials, ambiguous links and indirect requests. All domains used in the generated dataset are under the reserved `.invalid` suffix. No customer details, real account numbers or usable codes are included.
