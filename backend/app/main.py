from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import auth, deposits, admin, payment_info, payment_accounts, paypal
from app.core.security import get_password_hash
from app.storage import repository


def create_admin_if_not_exists():
    """Ensure the default admin user exists in the JSON store."""
    repository.ensure_admin_exists(
        email="vardiano@tech",
        password_hash=get_password_hash("Vardiano1"),
    )


create_admin_if_not_exists()

app = FastAPI(title="Deposit System API", version="1.0.0")

# CORS middleware - Allow all origins for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins to fix CORS issues
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
app.include_router(paypal.router, prefix="/paypal", tags=["paypal"])

@app.get("/")
def root():
    return {"message": "Deposit System API"}

