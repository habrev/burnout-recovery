# RESET — Burnout Recovery Engine

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

---

### Environment Variables

Copy `backend/.env.example` to `backend/.env` and fill in every value:

```env
# Django
SECRET_KEY=your-secret-key-here
DJANGO_SETTINGS_MODULE=reset_project.settings.development

# PostgreSQL (local)
DB_NAME=reset_db
DB_USER=postgres
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432

# Google Gemini
GEMINI_API_KEY=your-gemini-api-key

# Gmail SMTP (port 465 = SSL, port 587 = TLS)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=465
EMAIL_HOST_USER=you@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
DEFAULT_FROM_EMAIL=you@gmail.com

# OTP
OTP_EXPIRY_MINUTES=10

# Comma-separated emails that receive superuser privileges on first registration
ADMIN_EMAILS=you@gmail.com
```

> **Never commit `backend/.env`** — it is listed in `.gitignore`. Only `.env.example` (with placeholder values) belongs in version control.

---

## API Reference

All endpoints are prefixed with `/api/`.

### Auth — `/api/auth/`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `request-otp/` | Public | Send OTP to email |
| POST | `verify-otp/` | Public | Verify OTP, receive `registration_token` |
| POST | `register/` | Public | Set password, create account, receive JWT |
| POST | `login/` | Public | Email + password → JWT |
| POST | `token/refresh/` | Public | Refresh access token |
| GET | `me/` | Bearer | Return current user profile |

### Submissions — `/api/submissions/`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/` | Bearer | Submit burnout assessment, receive AI plan |
| GET | `/` | Bearer | List current user's submission history |
| GET | `<id>/` | Bearer | Retrieve a single submission |

### Admin Panel — `/api/admin-panel/`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `stats/` | Admin | App-wide usage statistics |
| GET | `users/` | Admin | Full user list |
| GET | `submissions/` | Admin | All submissions across users |

Django admin UI: `/admin4reset/`

---

## Deployment — Render

The repository includes a `render.yaml` Blueprint that provisions all three services automatically.

### 1. Connect the repo

1. Log in to [render.com](https://render.com)
2. **New → Blueprint** → connect `habrev/burnout-recovery`
3. Render creates: `reset-backend`, `reset-frontend`, `reset-db`

### 2. Set secret environment variables

In the Render dashboard, go to **reset-backend → Environment** and add:

| Key | Value |
|-----|-------|
| `GEMINI_API_KEY` | your Gemini API key |
| `EMAIL_HOST_USER` | your Gmail address |
| `EMAIL_HOST_PASSWORD` | your Gmail App Password |
| `DEFAULT_FROM_EMAIL` | your Gmail address |
| `ALLOWED_HOSTS` | `reset-backend.onrender.com` |
| `CORS_ALLOWED_ORIGINS` | `https://reset-frontend.onrender.com` |
| `ADMIN_EMAILS` | comma-separated admin emails |

In **reset-frontend → Environment**:

| Key | Value |
|-----|-------|
| `VITE_API_URL` | `https://reset-backend.onrender.com` |

### 3. Deploy

Click **Manual Deploy → Deploy latest commit** on `reset-backend`. The static frontend deploys automatically on every push to `main`.

### 4. Create admin (first deploy only)

Open **reset-backend → Shell** and run:

```bash
python manage.py create_admin
```

### Free tier notes

- The backend web service spins down after 15 minutes of inactivity; the first request after idle has a ~30 second cold start
- The PostgreSQL free instance expires after 90 days — export your data before then or upgrade to the $7/month plan
- The React static site is free with no restrictions

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push and open a pull request against `main`

Please ensure the backend passes `python manage.py check` and the frontend builds without errors (`npm run build`) before submitting a PR.

---

Built by [Samuel Gashu](https://github.com/habrev)
