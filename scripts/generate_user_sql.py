#!/usr/bin/env python3
"""
Generate SQL script with pre-hashed passwords for initial users
"""

from passlib.context import CryptContext

# Use bcrypt for password hashing (same as auth service)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Hash password using bcrypt"""
    if len(password.encode('utf-8')) > 72:
        password = password[:72]
    return pwd_context.hash(password)

USERS = [
    {"email": "admin@fintorg.ru", "password": "admin123", "role": "system_admin", "branch_id": 0},
    {"email": "manager@fintorg.ru", "password": "password123", "role": "manager", "branch_id": 0},
    {"email": "accountant@fintorg.ru", "password": "password123", "role": "accountant", "branch_id": 1},
    {"email": "accountant2@fintorg.ru", "password": "acc123", "role": "accountant", "branch_id": 2},
    {"email": "accountant3@fintorg.ru", "password": "acc123", "role": "accountant", "branch_id": 3},
]

def generate_sql():
    """Generate SQL INSERT statements"""
    sql_lines = [
        "-- Auto-generated SQL script for initial users",
        "-- This script inserts default users into auth_db",
        "",
        "\\c auth_db;",
        "",
        "-- Insert users (only if table exists and is empty)",
        "DO $$",
        "BEGIN",
        "    IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN",
        "        -- Insert users if they don't exist",
    ]
    
    for user in USERS:
        hashed = get_password_hash(user["password"])
        sql_lines.append(f"        IF NOT EXISTS (SELECT 1 FROM users WHERE email = '{user['email']}') THEN")
        sql_lines.append(f"            INSERT INTO users (email, hashed_password, role, branch_id, created_at)")
        sql_lines.append(f"            VALUES ('{user['email']}', '{hashed}', '{user['role']}', {user['branch_id']}, NOW());")
        sql_lines.append(f"        END IF;")
        sql_lines.append("")
    
    sql_lines.extend([
        "    END IF;",
        "END $$;",
        ""
    ])
    
    return "\n".join(sql_lines)

if __name__ == "__main__":
    sql = generate_sql()
    print(sql)
    
    # Also save to file
    with open("db-init/02-init-users.sql", "w") as f:
        f.write(sql)
    
    print("\n✅ SQL script generated and saved to db-init/02-init-users.sql")

