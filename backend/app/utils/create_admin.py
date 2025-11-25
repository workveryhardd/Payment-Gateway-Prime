"""
Script to create admin user
Run this once to create the admin user
"""
from app.core.security import get_password_hash
from app.storage import repository

def create_admin_user():
    """Ensure the default admin user exists when run manually."""
    repository.ensure_admin_exists(
        email="vardiano@tech",
        password_hash=get_password_hash("Vardiano1"),
    )
    print("✅ Admin user ensured (vardiano@tech / Vardiano1)")

if __name__ == "__main__":
    create_admin_user()

