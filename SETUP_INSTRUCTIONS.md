# Complete Setup Instructions - Deposit System

This guide will walk you through setting up and running the Deposit System from absolute scratch.

## Prerequisites

Before starting, make sure you have:

- ✅ **Python 3.8+** installed ([Download Python](https://www.python.org/downloads/))
- ✅ **Node.js 16+** and npm installed ([Download Node.js](https://nodejs.org/))
- ✅ **Git** installed (optional, for cloning)
- ✅ **Text Editor** (VS Code, PyCharm, etc.)

**Check if installed:**
```bash
python --version    # Should show Python 3.8+
node --version      # Should show v16+
npm --version       # Should show version number
```

---

## Part 1: Backend Setup (Python/FastAPI)

### Step 1: Navigate to Backend Directory

```bash
cd backend
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
```

**Linux/Mac:**
```bash
python3 -m venv venv
```

**What this does:** Creates an isolated Python environment for this project.

### Step 3: Activate Virtual Environment

**Windows (PowerShell):**
```bash
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```bash
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

**How to know it's activated:** You'll see `(venv)` at the start of your command prompt.

### Step 4: Install Python Dependencies

```bash
pip install -r requirements.txt
```

**What this installs:**
- FastAPI (web framework)
- SQLAlchemy (database ORM)
- Alembic (database migrations)
- Pydantic (data validation)
- And other required packages

**Expected output:** Should show "Successfully installed..." for all packages.

### Step 5: Configure Environment Variables

**Option A: Use the existing .env file (already created)**
```bash
# File already exists at: backend/.env
```

**Option B: Create from example**
```bash
# Copy the example file
copy .env.example .env    # Windows
cp .env.example .env      # Linux/Mac
```

**Edit `.env` file:**
```env
DATABASE_URL=sqlite:///./deposit_db.sqlite
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-change-in-production-min-32-chars
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Generate a secure SECRET_KEY (optional):**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```
Copy the output and paste it as `SECRET_KEY` in `.env`.

**Note:** 
- SQLite is already configured (no database server needed!)
- SECRET_KEY has a default value, so this step is optional

### Step 6: Run Database Migrations

```bash
alembic upgrade head
```

**What this does:**
- Creates the database file (`deposit_db.sqlite`)
- Creates all tables (users, deposits, incoming_ledger)

**Expected output:**
```
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Running upgrade  -> a429e3dbeb86, Initial migration
```

**Verify database was created:**
```bash
# Windows
dir deposit_db.sqlite

# Linux/Mac
ls -la deposit_db.sqlite
```

### Step 7: Start the Backend Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**What this does:**
- Starts the FastAPI server
- `--reload` enables auto-reload on code changes
- Server runs on `http://localhost:8000`

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Test the API:**
- Open browser: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

**Keep this terminal open!** The server needs to keep running.

---

## Part 2: Frontend Setup (React/TypeScript)

### Step 1: Open a New Terminal

**Important:** Keep the backend server running in the first terminal, open a new terminal window.

### Step 2: Navigate to Frontend Directory

```bash
cd frontend
```

### Step 3: Install Node Dependencies

```bash
npm install
```

**What this installs:**
- React
- TypeScript
- Vite (build tool)
- TailwindCSS
- Axios (HTTP client)
- And other required packages

**Expected output:** Should show "added X packages" and "audited X packages".

**Note:** This may take 2-5 minutes depending on your internet speed.

### Step 4: Configure API URL (Optional)

**Create `.env` file in frontend directory:**
```bash
# Windows
echo VITE_API_BASE_URL=http://localhost:8000 > .env

# Linux/Mac
echo "VITE_API_BASE_URL=http://localhost:8000" > .env
```

**Or manually create `.env` file with:**
```
VITE_API_BASE_URL=http://localhost:8000
```

**Note:** This is optional - it defaults to `http://localhost:8000` if not set.

### Step 5: Start the Frontend Development Server

```bash
npm run dev
```

**What this does:**
- Starts the Vite development server
- Compiles TypeScript and React code
- Serves the frontend on `http://localhost:5173`

**Expected output:**
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

**Open in browser:**
- Frontend: http://localhost:5173

---

## Part 3: Running Celery (Background Tasks) - Optional

Celery is used for automatic deposit matching. You can skip this for now if you just want to test the basic functionality.

### Step 1: Install Redis (Required for Celery)

**Windows:**
- Download from: https://github.com/microsoftarchive/redis/releases
- Or use WSL (Windows Subsystem for Linux)

**Linux:**
```bash
sudo apt-get install redis-server
```

**Mac:**
```bash
brew install redis
```

### Step 2: Start Redis Server

**Windows:**
```bash
redis-server
```

**Linux/Mac:**
```bash
redis-server
```

**Keep this terminal open!**

### Step 3: Start Celery Worker

**Open a new terminal, navigate to backend:**
```bash
cd backend
.\venv\Scripts\Activate.ps1    # Windows (activate venv)
# or
source venv/bin/activate       # Linux/Mac

celery -A app.core.celery_app worker --loglevel=info
```

### Step 4: Start Celery Beat (Scheduler)

**Open another new terminal, navigate to backend:**
```bash
cd backend
.\venv\Scripts\Activate.ps1    # Windows
# or
source venv/bin/activate       # Linux/Mac

celery -A app.core.celery_app beat --loglevel=info
```

---

## Part 4: Testing the Application

### Test Backend API

1. **Open API Documentation:**
   - Go to: http://localhost:8000/docs
   - This is an interactive API documentation

2. **Test Creating a Deposit:**
   - Click on `POST /deposits/create`
   - Click "Try it out"
   - Enter:
     ```json
     {
       "method": "UPI",
       "amount": 500.00
     }
     ```
   - Click "Execute"
   - Should return a deposit object with ID

3. **Test Getting Deposits:**
   - Click on `GET /deposits/my`
   - Click "Try it out"
   - Click "Execute"
   - Should return list of deposits

### Test Frontend

1. **Open Frontend:**
   - Go to: http://localhost:5173

2. **Note:** Authentication is currently disabled, so you can access all pages directly.

3. **Test Features:**
   - Create a deposit
   - View deposits
   - Submit UTR/proof
   - Access admin panel

---

## Quick Start Summary

**For Backend Only:**
```bash
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1    # Windows
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

**For Frontend Only:**
```bash
cd frontend
npm install
npm run dev
```

**For Both (2 terminals):**
```bash
# Terminal 1 - Backend
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd frontend
npm install
npm run dev
```

---

## Troubleshooting

### Backend Issues

**Problem: "Module not found"**
```bash
# Make sure virtual environment is activated
# Reinstall dependencies
pip install -r requirements.txt
```

**Problem: "Database locked"**
```bash
# Make sure only one process is accessing the database
# Close any database viewers
# Restart the server
```

**Problem: "Port 8000 already in use"**
```bash
# Change port
uvicorn app.main:app --reload --port 8001
```

### Frontend Issues

**Problem: "Cannot connect to API"**
```bash
# Check if backend is running on port 8000
# Check .env file has correct API URL
# Check CORS settings in backend
```

**Problem: "npm install fails"**
```bash
# Clear npm cache
npm cache clean --force
# Try again
npm install
```

**Problem: "Port 5173 already in use"**
```bash
# Vite will automatically use next available port
# Or specify port
npm run dev -- --port 5174
```

---

## Project Structure

```
Payment Gateway/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Configuration
│   │   ├── models/       # Database models
│   │   └── ...
│   ├── alembic/          # Database migrations
│   ├── .env              # Environment variables
│   ├── requirements.txt  # Python dependencies
│   └── deposit_db.sqlite # SQLite database (created after migration)
│
└── frontend/
    ├── src/
    │   ├── components/   # React components
    │   ├── pages/        # Page components
    │   └── ...
    ├── package.json      # Node dependencies
    └── .env              # Frontend environment variables
```

---

## Important Notes

1. **Authentication is DISABLED** - All endpoints are open for testing
2. **SQLite Database** - No database server needed, file is created automatically
3. **Development Mode** - Both servers run in development mode with hot-reload
4. **CORS Enabled** - Frontend can communicate with backend
5. **UPI Details** - Configure your UPI ID in `backend/app/assets/upi_details.txt` (see `backend/HOW_TO_CHANGE_UPI_DETAILS.md`)

---

## Next Steps

1. ✅ Backend running on http://localhost:8000
2. ✅ Frontend running on http://localhost:5173
3. ✅ Test creating deposits
4. ✅ Test API endpoints
5. ✅ Explore the admin panel

**You're all set! 🎉**

For questions or issues, check the API documentation at http://localhost:8000/docs

