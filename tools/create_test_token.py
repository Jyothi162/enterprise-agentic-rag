
import os
import sys
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv

load_dotenv()

SECRET = os.getenv("JWT_SECRET")

if not SECRET:
    raise RuntimeError("JWT_SECRET is missing from .env")

if len(sys.argv) != 2:
    raise SystemExit(
        "Usage: python -m tools.create_test_token admin"
    )

role = sys.argv[1].lower()

if role not in {"employee", "hr", "it", "admin"}:
    raise ValueError("Invalid role")

payload = {
    "sub": f"demo_{role}",
    "role": role,
    "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
}

token = jwt.encode(payload, SECRET, algorithm="HS256")

print("\nDEVELOPMENT TEST TOKEN:\n")
print(token)
print("\nExpires in 15 minutes.")
