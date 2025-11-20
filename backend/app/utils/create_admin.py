"""
Script to create admin user
Run this once to create the admin user
"""
from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

def create_admin_user():
    db = SessionLocal()
    try:
        # Check if admin already exists
        admin = db.query(User).filter(User.email == "vardiano@tech").first()
        if admin:
            print("Admin user already exists!")
            return
        
        # Create admin user
        admin_user = User(
            email="vardiano@tech",
            password_hash=get_password_hash("Vardiano1"),
            is_admin=True
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        print(f"✅ Admin user created successfully!")
        print(f"   Email: vardiano@tech")
        print(f"   Password: Vardiano1")
        print(f"   Admin: Yes")
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating admin user: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()

