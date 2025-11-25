# Deposit System - Project Summary

## Project Structure

```
Payment Gateway/
├── backend/
│   ├── alembic/
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   ├── alembic.ini
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── admin.py
│   │   │   ├── auth.py
│   │   │   └── deposits.py
│   │   ├── assets/
│   │   │   ├── bank_details.txt
│   │   │   ├── crypto_wallets.json
│   │   │   ├── upi_details.txt
│   │   │   ├── upi_qr.b64
│   │   │   └── samples/
│   │   │       ├── crypto/
│   │   │       │   ├── sample_erc20_tx.json
│   │   │       │   └── sample_trc20_tx.json
│   │   │       ├── emails/
│   │   │       │   ├── sample_imps_credit.eml
│   │   │       │   └── sample_upi_credit.eml
│   │   │       └── sms/
│   │   │           ├── sample_imps_sms.txt
│   │   │           └── sample_upi_sms.txt
│   │   ├── core/
│   │   │   ├── celery_app.py
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   └── security.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── deposit.py
│   │   │   ├── incoming_ledger.py
│   │   │   └── user.py
│   │   ├── parsers/
│   │   │   ├── __init__.py
│   │   │   ├── crypto_parser.py
│   │   │   ├── email_parser.py
│   │   │   └── sms_parser.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── deposit.py
│   │   │   ├── incoming_ledger.py
│   │   │   └── user.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── crypto_service.py
│   │   │   ├── deposits_service.py
│   │   │   └── ledger_matcher.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── logger.py
│   ├── README.md
│   └── requirements.txt
└── frontend/
    ├── index.html
    ├── package.json
    ├── postcss.config.cjs
    ├── README.md
    ├── tailwind.config.cjs
    ├── tsconfig.json
    ├── tsconfig.node.json
    ├── vite.config.ts
    └── src/
        ├── App.tsx
        ├── main.tsx
        ├── index.css
        ├── components/
        │   ├── DepositForm.tsx
        │   ├── DepositList.tsx
        │   ├── Layout.tsx
        │   └── StatusBadge.tsx
        ├── lib/
        │   ├── api.ts
        │   └── auth.ts
        └── pages/
            ├── AdminDepositsPage.tsx
            ├── DashboardPage.tsx
            ├── DepositPage.tsx
            └── LoginPage.tsx
```

## How to Run

### Backend

1. **Setup Virtual Environment:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your Redis URL, SECRET_KEY, and DATA_FILE_PATH
   ```

4. **Start FastAPI Server:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Start Celery Worker (in separate terminal):**
   ```bash
   celery -A app.core.celery_app worker --loglevel=info
   ```

6. **Start Celery Beat (in separate terminal):**
   ```bash
   celery -A app.core.celery_app beat --loglevel=info
   ```

### Frontend

1. **Install Dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Configure API URL (optional):**
   Create `.env` file:
   ```
   VITE_API_BASE_URL=http://localhost:8000
   ```

3. **Start Development Server:**
   ```bash
   npm run dev
   ```

   Frontend will be available at `http://localhost:5173`

## Example cURL Requests

### 1. Register a User

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "is_admin": false
  }'
```

### 2. Register an Admin User

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "admin123",
    "is_admin": true
  }'
```

### 3. Login

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

Response will include `access_token`. Save this token for subsequent requests.

### 4. Create a Deposit

```bash
curl -X POST "http://localhost:8000/deposits/create" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "method": "UPI",
    "amount": 500.00
  }'
```

### 5. Submit UTR/Proof

```bash
curl -X POST "http://localhost:8000/deposits/submit-proof" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "deposit_id": 1,
    "utr_or_hash": "234512345678"
  }'
```

### 6. Get My Deposits

```bash
curl -X GET "http://localhost:8000/deposits/my" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 7. Admin - List All Deposits

```bash
curl -X GET "http://localhost:8000/admin/deposits" \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN"
```

### 8. Admin - List Deposits by Status

```bash
curl -X GET "http://localhost:8000/admin/deposits?status=PENDING" \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN"
```

### 9. Admin - Approve Deposit

```bash
curl -X POST "http://localhost:8000/admin/deposits/1/approve" \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN"
```

### 10. Admin - Reject Deposit

```bash
curl -X POST "http://localhost:8000/admin/deposits/1/reject" \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN"
```

### 11. Admin - List Incoming Ledger Entries

```bash
curl -X GET "http://localhost:8000/admin/incoming-ledger?matched=false" \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN"
```

## Notes

- Replace `YOUR_ACCESS_TOKEN` and `ADMIN_ACCESS_TOKEN` with actual tokens from login responses
- The backend API documentation is available at `http://localhost:8000/docs` when the server is running
- Celery tasks automatically match pending deposits with ledger entries every 60 seconds
- Stale deposits (pending > 60 minutes) are automatically flagged every 5 minutes

