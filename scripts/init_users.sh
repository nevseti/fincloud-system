#!/bin/bash

# Script to initialize users in FinCloud system
# Usage: ./init_users.sh [auth-service-url]

AUTH_URL="${1:-http://localhost:8000}"

echo "🔐 Initializing users in FinCloud..."
echo "📡 Auth Service URL: $AUTH_URL"

# Function to register user
register_user() {
    local email=$1
    local password=$2
    local role=$3
    local branch_id=$4
    
    echo "📝 Registering: $email (role: $role, branch: $branch_id)"
    
    response=$(curl -s -w "\n%{http_code}" -X POST "$AUTH_URL/register" \
        -H "Content-Type: application/json" \
        -d "{
            \"email\": \"$email\",
            \"password\": \"$password\",
            \"role\": \"$role\",
            \"branch_id\": $branch_id
        }")
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -eq 200 ]; then
        echo "✅ Successfully registered: $email"
    elif [ "$http_code" -eq 400 ] && echo "$body" | grep -q "already registered"; then
        echo "⚠️  User already exists: $email (skipping)"
    else
        echo "❌ Failed to register $email (HTTP $http_code): $body"
    fi
    echo ""
}

# Register users
echo "👤 Registering Admin..."
register_user "admin@fintorg.ru" "admin123" "system_admin" 0

echo "👤 Registering Manager..."
register_user "manager@fintorg.ru" "password123" "manager" 0

echo "👤 Registering Accountant (Branch 1)..."
register_user "accountant@fintorg.ru" "password123" "accountant" 1

echo "👤 Registering Accountant (Branch 2)..."
register_user "accountant2@fintorg.ru" "acc123" "accountant" 2

echo "👤 Registering Accountant (Branch 3)..."
register_user "accountant3@fintorg.ru" "acc123" "accountant" 3

echo "✅ User initialization complete!"
echo ""
echo "📋 Summary:"
echo "  - Admin: admin@fintorg.ru / admin123"
echo "  - Manager: manager@fintorg.ru / password123"
echo "  - Accountant (Branch 1): accountant@fintorg.ru / password123"
echo "  - Accountant (Branch 2): accountant2@fintorg.ru / acc123"
echo "  - Accountant (Branch 3): accountant3@fintorg.ru / acc123"

