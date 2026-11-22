# Verification

From the project root, run `python -m pytest -q` with the backend environment active. The backend tests cover risk rules, fitted model loading, integrated risk signals, multilingual local explanations, input validation, and remote provider errors with a mocked SDK.

From `frontend/`, run `npm test` and `npm run build`. The tests cover sample selection, input reset, loading, duplicate-submit prevention and plain message/language submission.

## Smoke check

1. Start both servers without an API key. On the landing page, confirm the background moves and buttons respond to focus and hover.
2. Click **Get Started**. The navigation no longer displays that button. The analyzer shows a message field, language choices and sample buttons.
3. Paste your own synthetic message, such as “INR 662.75 was deposited in your account.” Select Hindi and analyze. Confirm the explanation and steps appear and the amount is shown.
4. Try the **OTP scam** sample and check that the displayed warning is actionable.
5. Check the mobile navigation and enable reduced motion. The moving background and button effects should stop.

Live provider output requires your own API key. The local explanation path and fitted classifier can both be used without one.

## Verified in this revision

- Backend tests: 39 passed. Frontend tests: 5 passed. TypeScript and production build passed.
- Chromium passed the landing animation, button hover, Get Started navigation, no-key Hindi analysis with the fitted model, high-risk warning, removed comparison route, mobile navigation and reduced-motion checks. Four routes were checked at 320, 390 and 768 CSS pixels.
- Live Gemini calls remain unverified. Provider behavior was exercised with mocks.
