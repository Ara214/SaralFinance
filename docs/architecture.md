# Architecture

The browser calls a FastAPI service over JSON. Gemini is invoked server-side and only the backend loads the API key. No app database, local storage or message logging is used. Successful and error responses set `Cache-Control: no-store`. Restrict the allowed origins to your frontend. If deploying outside localhost, configure HTTPS, authentication or a gateway quota to control access and cost.

## System architecture

```mermaid
flowchart TD
    A[React browser app] --> B[FastAPI]
    B --> C[Risk rules and Linear SVM]
    B --> D[Prompt builder]
    D --> E[Gemini API]
    E --> F[Pydantic validation]
    C --> G[Response assembly]
    F --> G
    G --> A
```

## Message analysis

```mermaid
flowchart TD
    A[Submit message and options] --> B{Valid input}
    B -->|No| C[Return validation error]
    B -->|Yes| D[Calculate risk]
    D --> E{Analysis mode}
    E -->|Gemini| F[Generate and validate explanation]
    E -->|Local or provider unavailable| G[Build a multilingual template explanation]
    F --> H[Return explanation and risk]
    G --> H
```

At the backend research comparison endpoint the API computes risk once and requests three explanations concurrently. It reports per-version errors if any versions succeed. Provider timeouts, rate limits and malformed output produce structured errors.

## Risk pipeline

```mermaid
flowchart TD
    A[Raw message] --> B[Mask explicit credential warnings]
    A --> C[Extract links without opening them]
    B --> D[Match weighted patterns]
    C --> D
    D --> E{Score}
    E -->|Below 25| F[Low]
    E -->|25 to 64| G[Medium]
    E -->|65 or higher| H[High]
    F --> I[Return localized result]
    G --> I
    H --> I
```

Each rule contributes at most once. The running analyzer also invokes the fitted char-TF-IDF Linear SVM. The final tier is the higher of the two component tiers. Scores are capped at 100. The URL rule treats links as unverified. It checks known shortening domains and recognizes one synthetic fixture domain. It never opens or authenticates a link.
