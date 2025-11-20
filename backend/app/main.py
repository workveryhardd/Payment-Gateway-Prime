from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.api import auth, deposits, admin, payment_info, payment_accounts

# Create tables
Base.metadata.create_all(bind=engine)

# Create admin user if not exists
from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

def create_admin_if_not_exists():
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.email == "vardiano@tech").first()
        if not admin:
            admin_user = User(
                email="vardiano@tech",
                password_hash=get_password_hash("Vardiano1"),
                is_admin=True
            )
            db.add(admin_user)
            db.commit()
            print("✅ Admin user created: vardiano@tech / Vardiano1")
    except Exception as e:
        print(f"Note: {e}")
    finally:
        db.close()

create_admin_if_not_exists()

app = FastAPI(title="Deposit System API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(deposits.router, prefix="/deposits", tags=["deposits"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(payment_info.router, prefix="/payment", tags=["payment"])
app.include_router(payment_accounts.router, prefix="/admin/payment-accounts", tags=["payment-accounts"])

@app.get("/")
def root():
    return {"message": "Deposit System API"}

