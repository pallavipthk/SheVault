<<<<<<< HEAD
# SHEVAULT AI - Digital Trust & Identity Protection Platform

> **"Verify first. Protect your identity. Participate safely."**

**SHEVAULT AI** is an AI-powered digital trust and identity defense platform purpose-built for women pursuing online career opportunities, freelance gigs, internships, scholarships, and campus roles. It analyzes incoming communications, contracts, and credential requests to shield users against predatory deposit traps, document extortion, and impersonation fraud.

---

## Architecture Overview

```
SheVault/
├── backend/
│   ├── app.py           # FastAPI ASGI entrypoint, routes, and static file serving
│   ├── trust_engine.py  # 5-module heuristic & deterministic scam detection engine
│   ├── ai_service.py    # Google Gemini LLM bridge with graceful trust engine fallback
│   ├── auth.py          # SQLite authentication, PBKDF2 salting/hashing & JWT tokens
│   ├── models.py        # Pydantic data schemas
│   └── test_suite.py    # End-to-end integration test runner
├── frontend/
│   ├── index.html       # Single-Page Application (SPA) with 11 specialized views
│   ├── app.css          # Botanical pastel design system & responsive UI
│   ├── app.js           # Client controller, state management & reactive interactions
│   └── hero-woman.jpg   # Brand hero visual asset
├── database/
│   └── shevault.db      # SQLite persistent storage
├── package.json         # NPM scripts runner for dev and test commands
├── requirements.txt     # Python dependencies
└── run.py               # Uvicorn server launcher (port 8000)
```

---

## Key Modules & Features

1. **5-Module Opportunity Black Box Analysis**:
   - **Asset Demand Evaluator**: Detects early requests for Aadhaar, PAN, passport scans, OTPs, or biometric selfies.
   - **Financial Trap Detector**: Flags refundable deposits, training fee traps, UPI handles (`@oksbi`, etc.), and crypto paywalls.
   - **Channel Integrity Examiner**: Pinpoints off-platform migration (Telegram, WhatsApp direct messaging) and suspicious domain extensions (`.xyz`, `.site`).
   - **Urgency & Psychological Coercion**: Detects countdown timers, breach penalty intimidation, and artificial scarcity.
   - **Corporate & Domain Validation**: Cross-checks corporate identity against spoofed brand personas.

2. **Verifiable Recruiter Pass**:
   - Generates shareable, zero-knowledge recruiter credential passes allowing candidates to safely establish verification before surrendering PII.

3. **Protect Me Now (Emergency Identity Exposure Triage)**:
   - Rapid-response incident recovery workflow with actionable push-back scripts, bank lock instructions, and cybercrime reporting guides.

4. **Campus Ambassador & Drive Verification**:
   - Student protection protocols validating campus placement drives, drive IDs, and corporate recruiters.

5. **Local Identity Firewall**:
   - Granular privacy policy controls restricting what identity tokens and documents can be transmitted.

---

## Quick Start

### 1. Requirements & Installation

- Python 3.10+
- Optional: Node.js 18+ (for running via npm scripts)

Install Python dependencies:
```bash
pip install -r requirements.txt
```

### 2. Launching the Platform

Using Python:
```bash
python run.py
```

Or using NPM:
```bash
npm start
```

Access the web interface in your browser:
👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## Demo Accounts

The database comes pre-seeded with test accounts (password for all demo accounts: `Password123!`):

| Name | Email | Role |
| :--- | :--- | :--- |
| **Ananya Sharma** | `ananya@shevault.ai` | Student |
| **Priya Patel** | `priya@shevault.ai` | Freelancer |
| **Ritu Sengupta** | `ritu@shevault.ai` | Job Seeker |

You can also create a new account directly from the **Get Started** modal.

---

## Running Automated Verification Tests

With the server running on `http://127.0.0.1:8000`:
```bash
python backend/test_suite.py
```
Or:
```bash
npm test
```
=======
# SheVault
>>>>>>> e75afa4d84788ff5f9daf84c81921eb000a3f5ca
