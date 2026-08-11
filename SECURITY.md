# Security Policy

## Reporting a Vulnerability

Do NOT open a public issue for security vulnerabilities.

Email: **hi@moltable.ai** with details. We respond within 48 hours.

## Scope

Moltable's security boundary covers the API server (`server/`), the web frontend (`web/`), and the Supabase data layer. We accept reports for:

- **Authentication & authorization bypass** — JWT verification, API keys (`molt_`), session tokens (`mol_`), and DID/VC verification (`verify_presentation`)
- **Data access without proper authorization** — including cross-tenant data exposure via Supabase Row Level Security (RLS) policy gaps or missing policies on user-owned tables
- **Injection attacks** — SQL, NoSQL, and prompt injection
- **API key, session token, or signing-key leakage or exposure** — including secrets committed to the repository (`.env`, `.env.production`, `MOLTABLE_ISSUER_KEY`, `API_KEY_PEPPER`, `DEEPSEEK_API_KEY`)
- **Session token storage & lifecycle** — how tokens are stored in the `sessions` table, expiry enforcement, and revocation
- **Cross-site scripting (XSS)** in the web frontend

## Out of Scope

- **Open redirects on known-safe URLs**
- **Theoretical attacks requiring physical access**

Note: The API already sets a full security header suite (`X-Content-Type-Options`, `X-Frame-Options`, `Strict-Transport-Security`, `Content-Security-Policy`, `Referrer-Policy`, `Permissions-Policy` in `server/main.py`). A regression in these headers should be reported as a regular issue, not a security report.

## Known Gaps

- **(Resolved)** `.env.production` was previously tracked in git (history now contains old key references). Rotated as of 2026-08-10; the file is now gitignored.

## Hall of Fame

We'll list researchers who responsibly disclose valid vulnerabilities here (with permission).
