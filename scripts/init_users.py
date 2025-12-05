#!/usr/bin/env python3
"""
Script to initialize users in FinCloud system
Usage: python init_users.py [auth-service-url]
"""

import sys
import requests
import json

AUTH_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"

USERS = [
    {"email": "admin@fintorg.ru", "password": "admin123", "role": "system_admin", "branch_id": 0},
    {"email": "manager@fintorg.ru", "password": "password123", "role": "manager", "branch_id": 0},
    {"email": "accountant@fintorg.ru", "password": "password123", "role": "accountant", "branch_id": 1},
    {"email": "accountant2@fintorg.ru", "password": "acc123", "role": "accountant", "branch_id": 2},
    {"email": "accountant3@fintorg.ru", "password": "acc123", "role": "accountant", "branch_id": 3},
]

def register_user(user_data):
    """Register a user via API"""
    email = user_data["email"]
    print(f"📝 Registering: {email} (role: {user_data['role']}, branch: {user_data['branch_id']})")
    
    try:
        response = requests.post(
            f"{AUTH_URL}/register",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print(f"✅ Successfully registered: {email}")
            return True
        elif response.status_code == 400 and "already registered" in response.text:
            print(f"⚠️  User already exists: {email} (skipping)")
            return True
        else:
            print(f"❌ Failed to register {email} (HTTP {response.status_code}): {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error registering {email}: {e}")
        return False

def main():
    print("🔐 Initializing users in FinCloud...")
    print(f"📡 Auth Service URL: {AUTH_URL}")
    print()
    
    success_count = 0
    for user in USERS:
        if register_user(user):
            success_count += 1
        print()
    
    print("✅ User initialization complete!")
    print()
    print("📋 Summary:")
    for user in USERS:
        print(f"  - {user['role']}: {user['email']} / {user['password']}")
    
    print(f"\n✅ Successfully processed {success_count}/{len(USERS)} users")

if __name__ == "__main__":
    main()

