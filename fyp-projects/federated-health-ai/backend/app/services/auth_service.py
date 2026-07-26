"""User registration and credential verification."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models import User
from app.services import audit_service


class EmailAlreadyRegistered(Exception):
    pass


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def register_user(db: Session, email: str, password: str, full_name: str) -> User:
    if get_user_by_email(db, email) is not None:
        raise EmailAlreadyRegistered(email)
    # First registered user becomes the platform admin.
    is_first = db.scalar(select(User.id).limit(1)) is None
    user = User(
        email=email,
        full_name=full_name,
        hashed_password=hash_password(password),
        role="admin" if is_first else "researcher",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    audit_service.record(db, email, "user.register", f"user:{user.id}")
    return user


def authenticate(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
    if user is None or not user.is_active:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
