# SaralFinance

**Finance, made simple.** A university prompt engineering project by **Team ZeroShot**.

Banking messages often compress an amount, a deadline and a request into one unclear alert. SaralFinance explains what a financial message claims, suggests practical verification steps and highlights suspicious signals. It supports English, Hindi and Hinglish. The analyzer sends only the message and language. The backend selects the prompt.

## Run locally

Use Python 3.11–3.13 and Node.js 22+. Run each block in its own terminal from the extracted project root.

### Backend (Windows PowerShell)

```powershell
cd backend
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --no-access-log
```

### Backend (macOS/Linux)

```bash
cd backend
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
cp .env.example .env
```

Edit `backend/.env` before starting the backend:

The bundled risk model and local multilingual explanations work with no API key. To enable richer online explanations, set `GEMINI_API_KEY` and optionally `GEMINI_MODEL`. The analyzer uses a local template explanation if the online service is unavailable.

```bash
# macOS/Linux, from backend/
.venv/bin/python -m uvicorn app.main:app --reload --no-access-log
```

### Frontend

```powershell
cd frontend
npm.cmd ci
npm.cmd run dev
```

On macOS/Linux use `npm` in place of `npm.cmd`. Visit [localhost:5173](http://localhost:5173). The frontend defaults to a backend at `http://127.0.0.1:8000`. If you change either origin, update `VITE_API_URL` and `FRONTEND_ORIGINS` as needed. The API docs are at [localhost:8000/docs](http://localhost:8000/docs).

## Features and stack

- React, TypeScript, Vite, Tailwind CSS, Motion, Lucide and React Router.
- FastAPI, Pydantic, Uvicorn, Python dotenv and Google's `google-genai` SDK.
- Dark plum landing page, responsive ivory workspace, keyboard controls and reduced motion.
- Explanation, next steps, localized risk signals and warnings, and an optional analogy.
- Risk screening combines the original explainable rules with the bundled Linear SVM. Either can raise the final tier. The numeric score in the API represents rule signals only.
- P0 applies a minimal instruction, P1 adds a financial literacy role and guidelines, and P2 adds six multilingual demonstrations. See [prompt methodology](docs/prompt_engineering.md).
- No database. The app does not store submitted messages. When configured, online explanations send submitted text to the provider. Use the synthetic examples or redact personal and secret details.

## API

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Show process and analysis mode |
| GET | `/api/prompts` | Backend research endpoint for prompt descriptions |
| GET | `/api/examples` | Load seven synthetic samples |
| POST | `/api/analyze` | Generate one explanation and calculate risk |
| POST | `/api/compare` | Backend research endpoint for three live prompt outputs and shared risk |

Send `{"message":"UPI alert: INR 480 debited for a payment to Demo Kirana.","language":"hinglish"}` to `/api/analyze`. The response includes explanation, next steps, risk reasons, and both component tiers. Provide a prompt version only for experiments that require an online model response.

## Evaluation and testing

From the project root with the backend environment active:

```bash
python dataset/generate_dataset.py
python -m evaluation.evaluate_risk
python -m evaluation.evaluate_risk --hybrid
python -m pytest -q
```

Use the virtual-environment Python executable directly if you prefer to avoid activation. From `frontend/`, run `npm test` and `npm run build` (or the `npm.cmd` equivalents).

The dataset has 300 unique synthetic records across eight categories. The 128-message holdout uses different scenario families from development. The rule engine reached **90.63% accuracy**, **0.878 macro F1** and **60% high-risk recall** on this holdout. See [evaluation methodology](docs/evaluation.md), [JSON metrics](evaluation/results/risk_evaluation.json) and [per-message decisions](evaluation/results/risk_evaluation.csv). The integrated rule + SVM screening reached **79.69% accuracy** and **100% high-risk recall**, flagging 26 other messages as high risk. See [hybrid metrics](evaluation/results/hybrid_evaluation.json) and [model notes](backend/ml/README.md). Backend prompt evaluation requires a live Gemini key and human ratings. The repository contains the workflow and rubric.

## Project layout

| Directory | Contents |
|---|---|
| `frontend/` | React app, API client, and component tests |
| `backend/` | API, online and local explanations, trained risk model and rules, prompt templates, backend tests |
| `dataset/` | Generator and synthetic message CSV |
| `evaluation/` | Risk and prompt evaluation tools and computed risk outputs |
| `docs/` | Architecture, prompt methods, evaluation and tests |

See [architecture](docs/architecture.md) and [verification](docs/testing.md).

## Limitations and future work

Risk predictions cannot authenticate senders or verify transactions. The combined policy raises more messages to high risk, including some legitimate-looking holdout examples. Local explanations include topic and amounts where recognizable and may omit details. Template-based synthetic metrics do not measure real-world fraud accuracy. LLM output may omit facts or give inaccurate explanations. The shared instructions, structured outputs and URL checks reduce risk, but prompt-injection resistance and multilingual quality need live evaluation. Future work could add a larger independently labeled set, more regional languages and an accessibility study.

Educational use only. Verify transactions, deadlines and account status through independently obtained official channels.
