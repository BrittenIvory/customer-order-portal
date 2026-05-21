# Customer Order Portal

A self-hosted web portal for customers to track their orders from production to delivery, integrated with MYOB Advanced ERP.

## Features

- **Customer login** — email/password authentication
- **Order dashboard** — view all orders with status filtering
- **Order detail** — see line-item-level status with a visual tracker
- **6-stage order tracking** tied to MYOB purchase orders and sales orders:
  1. **Waiting for Production** — PO exists, requested date > 3 weeks away
  2. **In Production** — within 3 weeks of PO requested date
  3. **In Transit to Warehouse** — PO requested date removed/blank
  4. **In Our Warehouse** — PO line received in MYOB
  5. **Inspected & Ready to Ship** — manually marked by admin
  6. **Shipped to Customer** — SO line invoiced
- **Admin panel** — manage customer accounts, link to MYOB customer IDs, mark items as inspected

## Tech Stack

| Layer    | Technology                    |
|----------|-------------------------------|
| Frontend | Next.js 16, React 19, Tailwind CSS 4 |
| Backend  | FastAPI, SQLAlchemy, PostgreSQL |
| Auth     | JWT (email/password)          |
| ERP      | MYOB Advanced (Acumatica REST API) |
| Hosting  | Docker Compose (self-hosted)  |

## Quick Start

### Prerequisites

- Docker and Docker Compose
- MYOB Advanced instance with API access

### 1. Clone and configure

```bash
git clone <repo-url>
cd customer-order-portal
cp .env.example .env
# Edit .env with your MYOB credentials and a secure SECRET_KEY
```

### 2. Start the services

```bash
docker compose up --build -d
```

This starts:
- **PostgreSQL** on port 5432
- **Backend API** on port 8000
- **Frontend** on port 3000

### 3. Log in

Open http://localhost:3000 and sign in with the default admin account:

- **Email:** `admin@milsonfoundry.com.au`
- **Password:** `changeme123`

> Change this password immediately after first login.

### 4. Set up customers

1. Go to the Admin panel
2. Create customer accounts with their email and MYOB Customer ID
3. Customers can then log in and see their orders

## Configuration

All configuration is via environment variables (see `.env.example`):

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | JWT signing secret (generate a random string) |
| `MYOB_BASE_URL` | Your MYOB Advanced instance URL |
| `MYOB_API_KEY` | MYOB API key |
| `MYOB_API_ID` | MYOB API/client ID |
| `MYOB_USERNAME` | MYOB API user login |
| `MYOB_PASSWORD` | MYOB API user password |
| `MYOB_COMPANY` | MYOB company name |
| `MYOB_BRANCH` | MYOB branch (optional) |

## Development

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/auth/login` | — | Login |
| GET | `/api/auth/me` | User | Current user info |
| POST | `/api/auth/change-password` | User | Change password |
| GET | `/api/orders` | User | List customer orders |
| GET | `/api/orders/{nbr}` | User | Order detail |
| GET | `/api/admin/users` | Admin | List users |
| POST | `/api/admin/users` | Admin | Create user |
| PUT | `/api/admin/users/{id}` | Admin | Update user |
| DELETE | `/api/admin/users/{id}` | Admin | Delete user |
| POST | `/api/admin/inspect` | Admin | Mark line inspected |
| DELETE | `/api/admin/inspect/{so}/{line}` | Admin | Unmark inspection |
| GET | `/api/health` | — | Health check |

## Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Customer   │────▶│   Next.js    │────▶│   FastAPI    │
│   Browser    │◀────│   Frontend   │◀────│   Backend    │
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                  │
                                    ┌─────────────┼──────────────┐
                                    │             │              │
                              ┌─────▼─────┐ ┌────▼────┐  ┌─────▼─────┐
                              │ PostgreSQL │ │  MYOB   │  │ Inspection│
                              │  (Users)   │ │Advanced │  │  Records  │
                              └───────────┘ └─────────┘  └───────────┘
```
