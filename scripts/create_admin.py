#!/usr/bin/env python3
"""Create the initial admin account for Moltable.

Usage:
  python scripts/create_admin.py --email admin@moltable.ai --password 'your-strong-password' --role admin

Requires SUPABASE_URL and SUPABASE_SERVICE_KEY in environment.
Run this once to bootstrap admin access.
"""
import os, sys, hashlib, secrets, argparse

def main():
    parser = argparse.ArgumentParser(description="Create a Moltable admin account")
    parser.add_argument("--email", required=True, help="Admin email")
    parser.add_argument("--password", required=True, help="Password (min 10 chars)")
    parser.add_argument("--role", choices=["admin", "operator"], default="admin")
    parser.add_argument("--name", default="", help="Display name")
    args = parser.parse_args()

    if len(args.password) < 10:
        print("❌ Password must be at least 10 characters")
        sys.exit(1)

    supabase_url = os.getenv("SUPABASE_URL", "")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY", "")

    if not supabase_url or not supabase_key:
        print("❌ SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
        sys.exit(1)

    try:
        from supabase import create_client
        client = create_client(supabase_url, supabase_key)
    except ImportError:
        # Fallback: use direct REST API
        print("supabase-py not installed. Use the SQL method instead:")
        print("""
  Run this in Supabase SQL Editor:
    INSERT INTO admin_users (email, name, password_hash, role)
    VALUES (
      '""" + args.email.lower().strip() + """',
      '""" + (args.name or args.email.split("@")[0]) + """',
      '""" + _hash_password(args.password, supabase_key) + """',
      '""" + args.role + """'
    );
        """)
        return

    pw_hash = _hash_password(args.password, supabase_key)
    name = args.name or args.email.split("@")[0]

    try:
        client.table("admin_users").insert({
            "email": args.email.lower().strip(),
            "name": name,
            "password_hash": pw_hash,
            "role": args.role,
            "is_active": True,
        }).execute()
        print(f"✅ Admin account created: {args.email} (role={args.role})")
    except Exception as e:
        err = str(e).lower()
        if "duplicate" in err or "unique" in err:
            print(f"⚠️  Account already exists: {args.email}")
        else:
            print(f"❌ Failed: {e}")
            sys.exit(1)


def _hash_password(password: str, pepper: str) -> str:
    salt = pepper[:16].encode()
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000).hex()


if __name__ == "__main__":
    main()
