<div align="center">

# 🛡️ SheVault AI

### Digital Trust & Identity Protection Platform

**_Verify first. Protect your identity. Participate safely._**

`Python 3.10+` · `FastAPI` · `SQLite` · `Google Gemini` · `Node.js 18+ (optional)`

</div>

---

## 📖 Overview

**SheVault AI** is an AI-powered digital trust and identity defense platform built for women pursuing **online jobs, freelance gigs, internships, scholarships, and campus roles**.

It analyzes incoming messages, offer letters, contracts, and credential requests, and shields users from:

- 💸 **Predatory deposit traps** (fake "refundable" fees, training charges)
- 🪪 **Document extortion** (premature Aadhaar / PAN / passport requests)
- 🎭 **Impersonation fraud** (spoofed brands and fake recruiters)

> Most scams succeed because the victim acts before verifying. SheVault flips that order: **verify first, share later.**

---

## 📑 Table of Contents

- [Key Features](#-key-features)
- [How the Trust Engine Works](#-how-the-trust-engine-works)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [Configuration](#-configuration)
- [Running Tests](#-running-tests)
- [Tech Stack](#-tech-stack)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)

---

## ✨ Key Features

| Feature | What it does |
|---|---|
| 🔍 **Opportunity Black Box Analysis** | Runs any offer or message through a 5-module scam detection engine and returns a clear risk verdict. |
| 🎫 **Verifiable Recruiter Pass** | Generates shareable, zero-knowledge recruiter credential passes so candidates can establish trust *before* surrendering personal data. |
| 🚨 **Protect Me Now** | Emergency identity-exposure triage with push-back scripts, bank-lock instructions, and cybercrime reporting guides. |
| 🎓 **Campus Ambassador & Drive Verification** | Validates campus placement drives, drive IDs, and corporate recruiters to protect students. |
| 🔒 **Local Identity Firewall** | Granular privacy controls that restrict which identity tokens and documents can be shared. |

---

## 🧠 How the Trust Engine Works

Every submission passes through five independent detection modules:

| # | Module | Detects |
|---|---|---|
| 1 | **Asset Demand Evaluator** | Early requests for Aadhaar, PAN, passport scans, OTPs, or biometric selfies. |
| 2 | **Financial Trap Detector** | Refundable deposits, training-fee traps, UPI handles (e.g. `@oksbi`), crypto paywalls. |
| 3 | **Channel Integrity Examiner** | Off-platform migration (Telegram, WhatsApp DMs) and suspicious domain extensions (`.xyz`, `.site`). |
| 4 | **Urgency & Psychological Coercion** | Countdown timers, breach-penalty intimidation, artificial scarcity. |
| 5 | **Corporate & Domain Validation** | Cross-checks the claimed company against spoofed brand personas. |

**Hybrid intelligence:** `ai_service.py` bridges to **Google Gemini** for deeper reasoning. If the LLM is unavailable, SheVault **gracefully falls back** to the deterministic trust engine, so protection never goes offline.

---

## 🏗️ Architecture

```
SheVault/
├── backend/
│   ├── app.py            # FastAPI ASGI entrypoint, routes, static file serving
│   ├── trust_engine.py   # 5-module heuristic & deterministic scam detection
│   ├── ai_service.py     # Gemini LLM bridge with trust-engine fallback
│   ├── auth.py           # SQLite auth, PBKDF2 salting/hashing, JWT tokens
│   ├── models.py         # Pydantic data schemas
│   └── test_suite.py     # End-to-end integration test runner
├── frontend/
│   ├── index.html        # Single-Page Application with 11 specialized views
│   ├── app.css           # Botanical pastel design system, responsive UI
│   ├── app.js            # Client controller, state management, interactions
│   └── hero-woman.jpg    # Brand hero visual asset
├── database/
│   └── shevault.db       # SQLite persistent storage
├── package.json          # NPM scripts for dev and test commands
├── requirements.txt      # Python dependencies
└── run.py                # Uvicorn server launcher (port 8000)
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+**
- *(Optional)* **Node.js 18+** to use the npm scripts

### 1. Clone & install

```bash
git clone <your-repo-url>
cd SheVault
pip install -r requirements.txt
```

### 2. Launch the platform

**With Python:**

```bash
python run.py
```

**Or with NPM:**

```bash
npm start
```

### 3. Open the app

👉 **http://127.0.0.1:8000**

Create your account from the **Get Started** modal to begin.

---

## ⚙️ Configuration

To enable Gemini-powered analysis, provide your API key as an environment variable:

```bash
export GEMINI_API_KEY="your-api-key"     # macOS / Linux
set GEMINI_API_KEY=your-api-key          # Windows (cmd)
```

> Check `backend/ai_service.py` for the exact variable name your setup expects. Without a key, SheVault runs entirely on the built-in trust engine.

---

## ✅ Running Tests

With the server running on `http://127.0.0.1:8000`:

```bash
python backend/test_suite.py
```

Or:

```bash
npm test
```

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI, Uvicorn |
| AI | Google Gemini + deterministic fallback engine |
| Auth | PBKDF2 salted hashing, JWT |
| Database | SQLite |
| Frontend | Vanilla HTML, CSS, JavaScript (SPA) |
| Tooling | NPM scripts (optional) |

---

## 🩺 Troubleshooting

| Problem | Fix |
|---|---|
| `Address already in use` on port 8000 | Stop the other process, or change the port in `run.py`. |
| Module import errors | Re-run `pip install -r requirements.txt` in your active environment. |
| Tests fail to connect | Make sure the server is running at `http://127.0.0.1:8000` first. |
| AI analysis seems basic | No Gemini key detected; the trust-engine fallback is active. |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add your feature"`
4. Run the test suite
5. Push and open a Pull Request

---

## 🔐 Security Note

SheVault is a decision-support tool. It reduces risk but cannot guarantee that any opportunity is safe. If you believe you have been defrauded, contact your bank immediately and report at **cybercrime.gov.in** or call **1930** (India's cybercrime helpline).

---

<div align="center">

**Verify first. Protect your identity. Participate safely.** 🛡️

</div>
