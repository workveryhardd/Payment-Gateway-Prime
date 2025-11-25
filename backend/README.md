# Deposit System Backend

A FastAPI-based backend for managing deposits across UPI, bank transfer, crypto, and credit/debit card flows with automatic ledger-based verification.

## Setup

### 1. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Copy `.env.example` to `.env` and update the values:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-change-in-production-min-32-chars
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATA_FILE_PATH=backend/data/data_store.json
```

**No database setup is required anymore.** All records (users, deposits, payment accounts, incoming ledger) are persisted inside the JSON file defined by `DATA_FILE_PATH`. The file and its parent directory are created automatically on first write.

### 4. Run the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

## Running Celery

### Start Redis

Make sure Redis is running:

```bash
redis-server
```

### Start Celery Worker

```bash
celery -A app.core.celery_app worker --loglevel=info
```

### Start Celery Beat (for periodic tasks)

```bash
celery -A app.core.celery_app beat --loglevel=info
```

## Project Structure

```
backend/
├── app/
│   ├── api/          # API endpoints
│   ├── core/         # Core configuration
│   ├── models/       # Domain enums shared across app
│   ├── schemas/      # Pydantic schemas
│   ├── services/     # Business logic
│   ├── storage/      # File-based JSON data store
│   ├── parsers/      # Email/SMS/Crypto parsers
│   ├── utils/        # Utilities
│   └── assets/       # Static assets and samples
└── requirements.txt
```

## API Endpoints

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login and get access token

### Deposits (requires authentication)
- `POST /deposits/create` - Create a new deposit
- `POST /deposits/submit-proof` - Submit UTR/hash for a deposit
- `GET /deposits/my` - Get current user's deposits

### Admin (requires admin authentication)
- `GET /admin/deposits` - List all deposits (with optional status filter)
- `POST /admin/deposits/{id}/approve` - Approve a deposit
- `POST /admin/deposits/{id}/reject` - Reject a deposit
- `GET /admin/incoming-ledger` - List incoming ledger entries

