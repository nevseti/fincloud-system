#!/usr/bin/env python3
"""
Quick script to generate bcrypt hashes for passwords
Run this once to get hashes, then use them in SQL
"""

try:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def hash_password(password: str) -> str:
        if len(password.encode('utf-8')) > 72:
            password = password[:72]
        return pwd_context.hash(password)
except ImportError:
    print("⚠️  passlib not installed. Installing...")
    import subprocess
    subprocess.check_call(["pip3", "install", "passlib[bcrypt]"])
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def hash_password(password: str) -> str:
        if len(password.encode('utf-8')) > 72:
            password = password[:72]
        return pwd_context.hash(password)

passwords = {
    "admin123": "admin123",
    "password123": "password123", 
    "acc123": "acc123"
}

print("🔐 Generated password hashes:")
print()
for name, password in passwords.items():
    hashed = hash_password(password)
    print(f"{name}: {hashed}")
    print()

