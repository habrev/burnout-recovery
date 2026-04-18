# RESET - Burnout Recovery Engine

A full-stack web application that assesses burnout severity and delivers AI-generated personalised recovery plans in real time. Built for high performers who need structured, evidence-informed interventions.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Key Features](#key-features)
- [Local Development](#local-development)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
  - [Environment Variables](#environment-variables)
- [API Reference](#api-reference)
- [Deployment — Render](#deployment--render)
- [Contributing](#contributing)

---

## Project Overview

RESET accepts a structured burnout assessment from the user (stress level, sleep quality, work hours, symptoms), runs it through a deterministic triage engine, then passes the result to **Google Gemini** (`gemini-3.0-flash`) to generate a contextualised recovery plan. Every submission and AI response is persisted to PostgreSQL for longitudinal tracking and admin review.

Authentication uses a three-step flow: email → OTP verification → password set. Returning users sign in with email and password. JSON Web Tokens (SimpleJWT) maintain sessions with automatic refresh.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite, Tailwind CSS, React Router v6, Axios |
| Backend | Django 5, Django REST Framework, SimpleJWT |
| Database | PostgreSQL (psycopg2) |
| AI | Google Gemini API (`google-genai` SDK) |
| Auth | Custom `AbstractBaseUser`, OTP email verification, JWT |
| Email | Gmail SMTP (port 465, SSL) |
| Deployment | Render (backend web service + static site + managed PostgreSQL) |

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│                  React Frontend                  │
│  LoginPage → BurnoutForm → ResultPage           │
│  AuthContext (JWT stored in localStorage)        │
└──────────────────────┬──────────────────────────┘
                       │ HTTPS / REST
┌──────────────────────▼──────────────────────────┐
│              Django REST Framework               │
│                                                  │
│  /api/auth/        — OTP + password auth         │
│  /api/submissions/ — burnout input + AI output   │
│  /api/admin-panel/ — admin stats & user list     │
│  /admin4reset/     — Django admin UI             │
└──────────┬──────────────────────┬───────────────┘
           │                      │
┌──────────▼──────┐    ┌──────────▼──────────────┐
│   PostgreSQL    │    │   Google Gemini API      │
│  (all models)   │    │  gemini-3.0-flash        │
└─────────────────┘    └─────────────────────────┘
```

**Apps:**
- `accounts` — custom user model, OTP tokens, auth views
- `submissions` — burnout form input, AI output, history
- `admin_panel` — restricted stats API for admin dashboard

---

## Key Features

- **Gemini AI recovery plans** — server-side only; API key never exposed to the client
- **Deterministic triage engine** — `engine.py` classifies stress level into three tiers and builds a structured prompt before calling Gemini
- **Persistent history** — every submission with its full AI response is saved and retrievable
- **Role-based access** — `ADMIN_EMAILS` env var auto-promotes specified addresses to superuser on registration
- **JWT with silent refresh** — Axios interceptor retries failed requests after refreshing the access token transparently

---

## Local Development

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+ running locally
- A Gmail account with an [App Password](https://myaccount.google.com/apppasswords) (2FA required)
- A [Google AI Studio](https://aistudio.google.com) API key for Gemini

---

### Backend Setup

```bash
# 1. Clone the repo
git clone https://github.com/habrev/burnout-recovery.git
cd burnout-recovery

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r backend/requirements.txt

# 4. Copy and fill in the env file
cp backend/.env.example backend/.env
# Edit backend/.env — see Environment Variables section below

# 5. Run migrations
cd backend
python manage.py migrate

# 6. Create admin user (optional — or register via the app with an ADMIN_EMAILS address)
python manage.py create_admin

# 7. Start the dev server
python manage.py runserver
```

Backend runs at `http://localhost:8000`

---

### Frontend Setup

```bash
cd frontend

# Install dependencies (includes Tailwind CSS, PostCSS, Autoprefixer)
npm install

# Start the dev server
npm run dev
```

Frontend runs at `http://localhost:5173`


## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push and open a pull request against `main`

Please ensure the backend passes `python manage.py check` and the frontend builds without errors (`npm run build`) before submitting a PR.

---

Built by [Samuel Gashu](https://github.com/habrev)
