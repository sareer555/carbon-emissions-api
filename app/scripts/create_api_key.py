"""Create a new API key.

Prints the PLAINTEXT key exactly once — only the SHA-256 hash is stored in
the database. If you lose the plaintext key, issue a new one.

Usage:
    python -m app.scripts.create_api_key --plan free --label "acme-inc"
    python -m app.scripts.create_api_key --plan starter --label "beta-customer-1"
"""
import argparse
import secrets

from app.auth import hash_key
from app.database import SessionLocal, init_db
from app.models import ApiKey


def create_api_key(plan: str, label: str | None) -> str:
    init_db()
    plaintext_key = f"cek_{secrets.token_urlsafe(32)}"  # "cek" = Carbon Emissions Key
    db = SessionLocal()
    try:
        db.add(ApiKey(key_hash=hash_key(plaintext_key), plan=plan, label=label))
        db.commit()
    finally:
        db.close()
    return plaintext_key


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", default="free", choices=["free", "starter", "growth", "scale"])
    parser.add_argument("--label", default=None, help="Human-readable owner/customer name")
    args = parser.parse_args()

    key = create_api_key(args.plan, args.label)
    print("API key created. Save this now — it will not be shown again:\n")
    print(f"  {key}\n")
    print(f"Plan: {args.plan}" + (f" | Label: {args.label}" if args.label else ""))
