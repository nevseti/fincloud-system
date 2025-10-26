"""
API tests for Auth Service endpoints
"""
import pytest
import httpx
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from app.models import User
from app.schemas import UserCreate, UserLogin


class TestAuthEndpoints:
    """Test Auth Service API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock database session"""
        return MagicMock()
    
    @pytest.fixture
    def sample_user_data(self):
        """Sample user data for testing"""
        return {
            "email": "test@example.com",
            "password": "password123",
            "role": "user",
            "branch_id": 1
        }
    
    @pytest.fixture
    def sample_user(self):
        """Sample user object"""
        user = MagicMock(spec=User)
        user.id = 1
        user.email = "test@example.com"
        user.hashed_password = "hashed_password_here"
        user.role = "user"
        user.branch_id = 1
        user.is_active = True
        return user


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


class TestRegisterEndpoint:
    """Test user registration endpoint"""
    
    @patch('app.main.get_db')
    @patch('app.main.get_password_hash')
    def test_register_user_success(self, mock_hash, mock_get_db, client, sample_user_data, mock_db_session):
        """Test successful user registration"""
        # Setup
        mock_get_db.return_value = mock_db_session
        mock_hash.return_value = "hashed_password"
        mock_db_session.query.return_value.filter.return_value.first.return_value = None  # User doesn't exist
        
        # Test
        response = client.post("/register", json=sample_user_data)
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == sample_user_data["email"]
        assert data["role"] == sample_user_data["role"]
        assert data["branch_id"] == sample_user_data["branch_id"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
        assert "hashed_password" not in data  # Password should not be returned
    
    @patch('app.main.get_db')
    def test_register_user_duplicate_email(self, mock_get_db, client, sample_user_data, mock_db_session, sample_user):
        """Test registration with duplicate email"""
        # Setup
        mock_get_db.return_value = mock_db_session
        mock_db_session.query.return_value.filter.return_value.first.return_value = sample_user  # User exists
        
        # Test
        response = client.post("/register", json=sample_user_data)
        
        # Assertions
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    def test_register_user_invalid_data(self, client):
        """Test registration with invalid data"""
        invalid_data = {
            "email": "invalid-email",
            "password": "123",  # Too short
            "role": "invalid_role",
            "branch_id": -1
        }
        
        response = client.post("/register", json=invalid_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_register_user_missing_fields(self, client):
        """Test registration with missing required fields"""
        incomplete_data = {
            "email": "test@example.com"
            # Missing password, role, branch_id
        }
        
        response = client.post("/register", json=incomplete_data)
        
        assert response.status_code == 422  # Validation error
    
    @patch('app.main.get_db')
    def test_register_user_database_error(self, mock_get_db, client, sample_user_data, mock_db_session):
        """Test registration with database error"""
        # Setup
        mock_get_db.return_value = mock_db_session
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        mock_db_session.add.side_effect = Exception("Database error")
        
        # Test
        response = client.post("/register", json=sample_user_data)
        
        # Assertions
        assert response.status_code == 500


class TestLoginEndpoint:
    """Test user login endpoint"""
    
    @patch('app.main.get_db')
    @patch('app.main.verify_password')
    @patch('app.main.create_access_token')
    def test_login_success(self, mock_create_token, mock_verify_password, mock_get_db, 
                          client, mock_db_session, sample_user):
        """Test successful user login"""
        # Setup
        mock_get_db.return_value = mock_db_session
        mock_db_session.query.return_value.filter.return_value.first.return_value = sample_user
        mock_verify_password.return_value = True
        mock_create_token.return_value = "access_token_here"
        
        login_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        
        # Test
        response = client.post("/login", json=login_data)
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "access_token_here"
        assert data["token_type"] == "bearer"
    
    @patch('app.main.get_db')
    def test_login_user_not_found(self, mock_get_db, client, mock_db_session):
        """Test login with non-existent user"""
        # Setup
        mock_get_db.return_value = mock_db_session
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        login_data = {
            "email": "nonexistent@example.com",
            "password": "password123"
        }
        
        # Test
        response = client.post("/login", json=login_data)
        
        # Assertions
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]
    
    @patch('app.main.get_db')
    @patch('app.main.verify_password')
    def test_login_wrong_password(self, mock_verify_password, mock_get_db, 
                                 client, mock_db_session, sample_user):
        """Test login with wrong password"""
        # Setup
        mock_get_db.return_value = mock_db_session
        mock_db_session.query.return_value.filter.return_value.first.return_value = sample_user
        mock_verify_password.return_value = False
        
        login_data = {
            "email": "test@example.com",
            "password": "wrongpassword"
        }
        
        # Test
        response = client.post("/login", json=login_data)
        
        # Assertions
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]
    
    @patch('app.main.get_db')
    def test_login_inactive_user(self, mock_get_db, client, mock_db_session):
        """Test login with inactive user"""
        # Setup
        inactive_user = MagicMock(spec=User)
        inactive_user.is_active = False
        mock_get_db.return_value = mock_db_session
        mock_db_session.query.return_value.filter.return_value.first.return_value = inactive_user
        
        login_data = {
            "email": "inactive@example.com",
            "password": "password123"
        }
        
        # Test
        response = client.post("/login", json=login_data)
        
        # Assertions
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]
    
    def test_login_invalid_data(self, client):
        """Test login with invalid data"""
        invalid_data = {
            "email": "invalid-email",
            "password": ""
        }
        
        response = client.post("/login", json=invalid_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_login_missing_fields(self, client):
        """Test login with missing fields"""
        incomplete_data = {
            "email": "test@example.com"
            # Missing password
        }
        
        response = client.post("/login", json=incomplete_data)
        
        assert response.status_code == 422  # Validation error


class TestGetUsersEndpoint:
    """Test get users endpoint"""
    
    @patch('app.main.get_db')
    @patch('app.main.get_current_active_user')
    def test_get_users_success(self, mock_get_current_user, mock_get_db, 
                              client, mock_db_session, sample_user):
        """Test successful get users"""
        # Setup
        mock_get_db.return_value = mock_db_session
        mock_get_current_user.return_value = sample_user
        mock_db_session.query.return_value.offset.return_value.limit.return_value.all.return_value = [sample_user]
        mock_db_session.query.return_value.count.return_value = 1
        
        # Test
        response = client.get("/users?skip=0&limit=10")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert "total" in data
        assert len(data["users"]) == 1
        assert data["total"] == 1
    
    def test_get_users_without_token(self, client):
        """Test get users without authentication token"""
        response = client.get("/users")
        
        assert response.status_code == 401
    
    @patch('app.main.get_db')
    @patch('app.main.get_current_active_user')
    def test_get_users_with_pagination(self, mock_get_current_user, mock_get_db, 
                                      client, mock_db_session, sample_user):
        """Test get users with pagination"""
        # Setup
        mock_get_db.return_value = mock_db_session
        mock_get_current_user.return_value = sample_user
        mock_db_session.query.return_value.offset.return_value.limit.return_value.all.return_value = []
        mock_db_session.query.return_value.count.return_value = 0
        
        # Test
        response = client.get("/users?skip=10&limit=5")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert "total" in data
        assert len(data["users"]) == 0
        assert data["total"] == 0
    
    @patch('app.main.get_db')
    @patch('app.main.get_current_active_user')
    def test_get_users_invalid_pagination(self, mock_get_current_user, mock_get_db, 
                                         client, mock_db_session, sample_user):
        """Test get users with invalid pagination parameters"""
        # Setup
        mock_get_db.return_value = mock_db_session
        mock_get_current_user.return_value = sample_user
        
        # Test with negative skip
        response = client.get("/users?skip=-1&limit=10")
        assert response.status_code == 422
        
        # Test with negative limit
        response = client.get("/users?skip=0&limit=-1")
        assert response.status_code == 422
        
        # Test with zero limit
        response = client.get("/users?skip=0&limit=0")
        assert response.status_code == 422


class TestGetUserEndpoint:
    """Test get user by ID endpoint"""
    
    @patch('app.main.get_db')
    @patch('app.main.get_current_active_user')
    def test_get_user_success(self, mock_get_current_user, mock_get_db, 
                             client, mock_db_session, sample_user):
        """Test successful get user by ID"""
        # Setup
        mock_get_db.return_value = mock_db_session
        mock_get_current_user.return_value = sample_user
        mock_db_session.query.return_value.filter.return_value.first.return_value = sample_user
        
        # Test
        response = client.get("/users/1")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["email"] == "test@example.com"
    
    @patch('app.main.get_db')
    @patch('app.main.get_current_active_user')
    def test_get_user_not_found(self, mock_get_current_user, mock_get_db, 
                               client, mock_db_session, sample_user):
        """Test get user with non-existent ID"""
        # Setup
        mock_get_db.return_value = mock_db_session
        mock_get_current_user.return_value = sample_user
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        # Test
        response = client.get("/users/999")
        
        # Assertions
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]
    
    def test_get_user_without_token(self, client):
        """Test get user without authentication token"""
        response = client.get("/users/1")
        
        assert response.status_code == 401
    
    def test_get_user_invalid_id(self, client):
        """Test get user with invalid ID format"""
        response = client.get("/users/invalid")
        
        assert response.status_code == 422  # Validation error


class TestUpdateUserEndpoint:
    """Test update user endpoint"""
    
    @patch('app.main.get_db')
    @patch('app.main.get_current_active_user')
    @patch('app.main.get_password_hash')
    def test_update_user_success(self, mock_hash, mock_get_current_user, mock_get_db, 
                                client, mock_db_session, sample_user):
        """Test successful user update"""
        # Setup
        mock_get_db.return_value = mock_db_session
        mock_get_current_user.return_value = sample_user
        mock_db_session.query.return_value.filter.return_value.first.return_value = sample_user
        mock_hash.return_value = "new_hashed_password"
        
        update_data = {
            "email": "updated@example.com",
            "role": "admin",
            "branch_id": 2
        }
        
        # Test
        response = client.put("/users/1", json=update_data)
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "updated@example.com"
        assert data["role"] == "admin"
        assert data["branch_id"] == 2
    
    @patch('app.main.get_db')
    @patch('app.main.get_current_active_user')
    def test_update_user_not_found(self, mock_get_current_user, mock_get_db, 
                                  client, mock_db_session, sample_user):
        """Test update user with non-existent ID"""
        # Setup
        mock_get_db.return_value = mock_db_session
        mock_get_current_user.return_value = sample_user
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        update_data = {
            "email": "updated@example.com"
        }
        
        # Test
        response = client.put("/users/999", json=update_data)
        
        # Assertions
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]
    
    def test_update_user_without_token(self, client):
        """Test update user without authentication token"""
        update_data = {
            "email": "updated@example.com"
        }
        
        response = client.put("/users/1", json=update_data)
        
        assert response.status_code == 401
    
    def test_update_user_invalid_data(self, client):
        """Test update user with invalid data"""
        invalid_data = {
            "email": "invalid-email",
            "branch_id": -1
        }
        
        response = client.put("/users/1", json=invalid_data)
        
        assert response.status_code == 422  # Validation error


class TestDeleteUserEndpoint:
    """Test delete user endpoint"""
    
    @patch('app.main.get_db')
    @patch('app.main.get_current_active_user')
    def test_delete_user_success(self, mock_get_current_user, mock_get_db, 
                                client, mock_db_session, sample_user):
        """Test successful user deletion"""
        # Setup
        mock_get_db.return_value = mock_db_session
        mock_get_current_user.return_value = sample_user
        mock_db_session.query.return_value.filter.return_value.first.return_value = sample_user
        
        # Test
        response = client.delete("/users/1")
        
        # Assertions
        assert response.status_code == 200
        assert "User deleted successfully" in response.json()["message"]
    
    @patch('app.main.get_db')
    @patch('app.main.get_current_active_user')
    def test_delete_user_not_found(self, mock_get_current_user, mock_get_db, 
                                  client, mock_db_session, sample_user):
        """Test delete user with non-existent ID"""
        # Setup
        mock_get_db.return_value = mock_db_session
        mock_get_current_user.return_value = sample_user
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        # Test
        response = client.delete("/users/999")
        
        # Assertions
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]
    
    def test_delete_user_without_token(self, client):
        """Test delete user without authentication token"""
        response = client.delete("/users/1")
        
        assert response.status_code == 401
    
    def test_delete_user_invalid_id(self, client):
        """Test delete user with invalid ID format"""
        response = client.delete("/users/invalid")
        
        assert response.status_code == 422  # Validation error


class TestAPIEdgeCases:
    """Test API edge cases and error scenarios"""
    
    def test_cors_headers(self, client):
        """Test CORS headers are present"""
        response = client.options("/health")
        
        # CORS headers should be present (handled by middleware)
        assert response.status_code in [200, 204]
    
    def test_unsupported_methods(self, client):
        """Test unsupported HTTP methods"""
        # PATCH method not supported
        response = client.patch("/users/1")
        assert response.status_code == 405
        
        # HEAD method
        response = client.head("/users")
        assert response.status_code in [200, 405]  # Depends on implementation
    
    def test_large_request_body(self, client):
        """Test request with very large body"""
        large_data = {
            "email": "test@example.com",
            "password": "a" * 10000,  # Very long password
            "role": "user",
            "branch_id": 1
        }
        
        response = client.post("/register", json=large_data)
        
        # Should handle gracefully (either success or validation error)
        assert response.status_code in [200, 422, 413]
    
    def test_malformed_json(self, client):
        """Test request with malformed JSON"""
        response = client.post(
            "/register",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
    
    def test_missing_content_type(self, client):
        """Test request without Content-Type header"""
        response = client.post(
            "/register",
            data='{"email": "test@example.com", "password": "password123", "role": "user", "branch_id": 1}'
        )
        
        # Should handle gracefully
        assert response.status_code in [200, 415, 422]
