"""Explicit operator-only identity provisioning. Never accepts passwords in arguments."""

import argparse
import getpass

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.entities import Audit, Organisation, User
from app.security.auth import passwords


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--organisation", required=True)
    parser.add_argument("--email", required=True)
    parser.add_argument("--role", choices=["admin", "reviewer", "analyst", "viewer"], required=True)
    args = parser.parse_args()
    password = getpass.getpass("New password (16+ characters): ")
    if len(password) < 16 or password != getpass.getpass("Repeat password: "):
        raise SystemExit("Passwords must match and contain 16+ characters")
    with SessionLocal() as db:
        org = db.scalar(select(Organisation).where(Organisation.name == args.organisation))
        if not org:
            org = Organisation(name=args.organisation, synthetic=False)
            db.add(org)
            db.flush()
        user = User(
            org_id=org.id, email=args.email, role=args.role, password_hash=passwords.hash(password)
        )
        db.add(user)
        db.flush()
        db.add(
            Audit(
                org_id=org.id,
                actor_id="operator",
                action="identity.provisioned",
                record_id=user.id,
                detail={"role": user.role},
            )
        )
        db.commit()
    print("Identity provisioned")


if __name__ == "__main__":
    main()
