"""Seed script to create initial admin user."""

import sys

from app.core.security import get_password_hash
from app.database import SessionLocal
from app.models.user import User


def seed():
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.is_admin.is_(True)).first()
        if admin:
            print(f"Admin user already exists: {admin.email}")
            return

        admin = User(
            email="admin@milsonfoundry.com.au",
            hashed_password=get_password_hash("changeme123"),
            full_name="Admin",
            company_name="Milson Foundry",
            is_admin=True,
            is_active=True,
        )
        db.add(admin)
        db.commit()
        print(f"Created admin user: {admin.email} (password: changeme123)")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
