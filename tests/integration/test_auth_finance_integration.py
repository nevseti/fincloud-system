"""
Integration tests between Auth Service and Finance Service
"""
import pytest
import httpx
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import User, Base
from app.database import get_db
from app.main import app
from fastapi.testclient import TestClient


class TestAuthFinanceIntegration:
    """Test integration between Auth and Finance services"""
    
    @pytest.fixture(scope="class")
    def test_db(self):
        """Create test database"""
        engine = create_engine("sqlite:///./test_integration.db")
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        return SessionLocal()
    
    @pytest.fixture
    def client(self, test_db):
        """Create test client with test database"""
        def override_get_db():
            try:
                yield test_db
            finally:
                pass
        
        app.dependency_overrides[get_db] = override_get_db
        client = TestClient(app)
        yield client
        app.dependency_overrides.clear()
    
    @pytest.fixture
    def auth_token(self, client):
        """Create a test user and get auth token"""
        # Register user
        user_data = {
            "email": "test@example.com",
            "password": "password123",
            "role": "user",
            "branch_id": 1
        }
        
        response = client.post("/register", json=user_data)
        assert response.status_code == 200
        
        # Login to get token
        login_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        
        response = client.post("/login", json=login_data)
        assert response.status_code == 200
        
        token_data = response.json()
        return token_data["access_token"]
    
    def test_user_registration_and_login_flow(self, client):
        """Test complete user registration and login flow"""
        # Step 1: Register user
        user_data = {
            "email": "integration@example.com",
            "password": "password123",
            "role": "user",
            "branch_id": 1
        }
        
        response = client.post("/register", json=user_data)
        assert response.status_code == 200
        
        user_response = response.json()
        assert user_response["email"] == "integration@example.com"
        assert user_response["role"] == "user"
        assert user_response["branch_id"] == 1
        assert "id" in user_response
        
        # Step 2: Login with registered user
        login_data = {
            "email": "integration@example.com",
            "password": "password123"
        }
        
        response = client.post("/login", json=login_data)
        assert response.status_code == 200
        
        token_data = response.json()
        assert "access_token" in token_data
        assert token_data["token_type"] == "bearer"
        
        # Step 3: Use token to access protected endpoint
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        response = client.get("/users", headers=headers)
        assert response.status_code == 200
    
    def test_token_authentication_flow(self, client, auth_token):
        """Test token-based authentication flow"""
        # Test accessing protected endpoint with valid token
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = client.get("/users", headers=headers)
        assert response.status_code == 200
        
        # Test accessing protected endpoint without token
        response = client.get("/users")
        assert response.status_code == 401
        
        # Test accessing protected endpoint with invalid token
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/users", headers=headers)
        assert response.status_code == 401
    
    def test_user_management_flow(self, client, auth_token):
        """Test complete user management flow"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Step 1: Get all users
        response = client.get("/users", headers=headers)
        assert response.status_code == 200
        users_data = response.json()
        initial_count = users_data["total"]
        
        # Step 2: Create new user
        new_user_data = {
            "email": "newuser@example.com",
            "password": "password123",
            "role": "user",
            "branch_id": 2
        }
        
        response = client.post("/register", json=new_user_data)
        assert response.status_code == 200
        
        # Step 3: Verify user count increased
        response = client.get("/users", headers=headers)
        assert response.status_code == 200
        users_data = response.json()
        assert users_data["total"] == initial_count + 1
        
        # Step 4: Get specific user
        new_user = response.json()["users"][-1]  # Get the last user (newly created)
        user_id = new_user["id"]
        
        response = client.get(f"/users/{user_id}", headers=headers)
        assert response.status_code == 200
        user_data = response.json()
        assert user_data["email"] == "newuser@example.com"
        
        # Step 5: Update user
        update_data = {
            "role": "admin",
            "branch_id": 3
        }
        
        response = client.put(f"/users/{user_id}", json=update_data, headers=headers)
        assert response.status_code == 200
        updated_user = response.json()
        assert updated_user["role"] == "admin"
        assert updated_user["branch_id"] == 3
        
        # Step 6: Delete user
        response = client.delete(f"/users/{user_id}", headers=headers)
        assert response.status_code == 200
        
        # Step 7: Verify user count decreased
        response = client.get("/users", headers=headers)
        assert response.status_code == 200
        users_data = response.json()
        assert users_data["total"] == initial_count
    
    def test_multiple_users_different_roles(self, client):
        """Test creating and managing users with different roles"""
        roles = ["user", "admin", "manager", "system_admin"]
        created_users = []
        
        # Create users with different roles
        for i, role in enumerate(roles):
            user_data = {
                "email": f"{role}@example.com",
                "password": "password123",
                "role": role,
                "branch_id": i + 1
            }
            
            response = client.post("/register", json=user_data)
            assert response.status_code == 200
            created_users.append(response.json())
        
        # Login as each user and verify their role
        for user_data in created_users:
            login_data = {
                "email": user_data["email"],
                "password": "password123"
            }
            
            response = client.post("/login", json=login_data)
            assert response.status_code == 200
            
            token_data = response.json()
            headers = {"Authorization": f"Bearer {token_data['access_token']}"}
            
            # Each user should be able to access their own data
            response = client.get("/users", headers=headers)
            assert response.status_code == 200
    
    def test_user_branch_assignment(self, client):
        """Test user assignment to different branches"""
        branch_ids = [1, 2, 3, 10, 100]
        created_users = []
        
        # Create users in different branches
        for branch_id in branch_ids:
            user_data = {
                "email": f"user_branch_{branch_id}@example.com",
                "password": "password123",
                "role": "user",
                "branch_id": branch_id
            }
            
            response = client.post("/register", json=user_data)
            assert response.status_code == 200
            created_users.append(response.json())
        
        # Verify all users were created with correct branch assignments
        for user_data in created_users:
            assert user_data["branch_id"] in branch_ids
    
    def test_password_security_flow(self, client):
        """Test password security and hashing"""
        user_data = {
            "email": "security@example.com",
            "password": "SecurePassword123!@#",
            "role": "user",
            "branch_id": 1
        }
        
        # Register user
        response = client.post("/register", json=user_data)
        assert response.status_code == 200
        
        # Verify password is not returned in response
        user_response = response.json()
        assert "password" not in user_response
        assert "hashed_password" not in user_response
        
        # Login with correct password
        login_data = {
            "email": "security@example.com",
            "password": "SecurePassword123!@#"
        }
        
        response = client.post("/login", json=login_data)
        assert response.status_code == 200
        
        # Try login with wrong password
        wrong_login_data = {
            "email": "security@example.com",
            "password": "WrongPassword123"
        }
        
        response = client.post("/login", json=wrong_login_data)
        assert response.status_code == 401
    
    def test_concurrent_user_operations(self, client):
        """Test concurrent user operations"""
        import threading
        import time
        
        results = []
        
        def create_user(user_id):
            user_data = {
                "email": f"concurrent_{user_id}@example.com",
                "password": "password123",
                "role": "user",
                "branch_id": 1
            }
            
            response = client.post("/register", json=user_data)
            results.append((user_id, response.status_code))
        
        # Create multiple users concurrently
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_user, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all users were created successfully
        assert len(results) == 5
        for user_id, status_code in results:
            assert status_code == 200
    
    def test_error_handling_flow(self, client):
        """Test error handling in various scenarios"""
        # Test duplicate email registration
        user_data = {
            "email": "duplicate@example.com",
            "password": "password123",
            "role": "user",
            "branch_id": 1
        }
        
        # First registration should succeed
        response = client.post("/register", json=user_data)
        assert response.status_code == 200
        
        # Second registration with same email should fail
        response = client.post("/register", json=user_data)
        assert response.status_code == 400
        
        # Test login with non-existent user
        login_data = {
            "email": "nonexistent@example.com",
            "password": "password123"
        }
        
        response = client.post("/login", json=login_data)
        assert response.status_code == 401
        
        # Test accessing protected endpoint without token
        response = client.get("/users")
        assert response.status_code == 401
        
        # Test accessing non-existent user
        headers = {"Authorization": "Bearer valid_token_format_but_invalid"}
        response = client.get("/users/999", headers=headers)
        assert response.status_code == 401  # Invalid token
    
    def test_data_consistency_flow(self, client):
        """Test data consistency across operations"""
        # Create user
        user_data = {
            "email": "consistency@example.com",
            "password": "password123",
            "role": "user",
            "branch_id": 1
        }
        
        response = client.post("/register", json=user_data)
        assert response.status_code == 200
        created_user = response.json()
        user_id = created_user["id"]
        
        # Login to get token
        login_data = {
            "email": "consistency@example.com",
            "password": "password123"
        }
        
        response = client.post("/login", json=login_data)
        assert response.status_code == 200
        token_data = response.json()
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        
        # Verify user data consistency
        response = client.get(f"/users/{user_id}", headers=headers)
        assert response.status_code == 200
        retrieved_user = response.json()
        
        # Data should be consistent
        assert retrieved_user["id"] == created_user["id"]
        assert retrieved_user["email"] == created_user["email"]
        assert retrieved_user["role"] == created_user["role"]
        assert retrieved_user["branch_id"] == created_user["branch_id"]
        assert retrieved_user["is_active"] == created_user["is_active"]
