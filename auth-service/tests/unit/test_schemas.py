"""
Unit tests for schemas.py - testing Pydantic models
"""
import pytest
from datetime import datetime
from pydantic import ValidationError
from app.schemas import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserLogin,
    Token,
    TokenData
)


class TestUserCreate:
    """Test UserCreate schema validation"""
    
    def test_user_create_valid(self):
        """Test valid user creation data"""
        user_data = {
            "email": "test@example.com",
            "password": "password123",
            "role": "user",
            "branch_id": 1
        }
        
        user = UserCreate(**user_data)
        
        assert user.email == "test@example.com"
        assert user.password == "password123"
        assert user.role == "user"
        assert user.branch_id == 1
    
    def test_user_create_missing_email(self):
        """Test user creation with missing email"""
        user_data = {
            "password": "password123",
            "role": "user",
            "branch_id": 1
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)
        
        assert "email" in str(exc_info.value)
    
    def test_user_create_missing_password(self):
        """Test user creation with missing password"""
        user_data = {
            "email": "test@example.com",
            "role": "user",
            "branch_id": 1
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)
        
        assert "password" in str(exc_info.value)
    
    def test_user_create_missing_role(self):
        """Test user creation with missing role"""
        user_data = {
            "email": "test@example.com",
            "password": "password123",
            "branch_id": 1
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)
        
        assert "role" in str(exc_info.value)
    
    def test_user_create_missing_branch_id(self):
        """Test user creation with missing branch_id"""
        user_data = {
            "email": "test@example.com",
            "password": "password123",
            "role": "user"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)
        
        assert "branch_id" in str(exc_info.value)
    
    def test_user_create_invalid_email_format(self):
        """Test user creation with invalid email format"""
        user_data = {
            "email": "invalid-email",
            "password": "password123",
            "role": "user",
            "branch_id": 1
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)
        
        assert "email" in str(exc_info.value)
    
    def test_user_create_empty_email(self):
        """Test user creation with empty email"""
        user_data = {
            "email": "",
            "password": "password123",
            "role": "user",
            "branch_id": 1
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)
        
        assert "email" in str(exc_info.value)
    
    def test_user_create_empty_password(self):
        """Test user creation with empty password"""
        user_data = {
            "email": "test@example.com",
            "password": "",
            "role": "user",
            "branch_id": 1
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)
        
        assert "password" in str(exc_info.value)
    
    def test_user_create_different_roles(self):
        """Test user creation with different valid roles"""
        roles = ["user", "admin", "manager", "system_admin"]
        
        for role in roles:
            user_data = {
                "email": f"test_{role}@example.com",
                "password": "password123",
                "role": role,
                "branch_id": 1
            }
            
            user = UserCreate(**user_data)
            assert user.role == role
    
    def test_user_create_different_branch_ids(self):
        """Test user creation with different branch IDs"""
        branch_ids = [1, 2, 3, 10, 100]
        
        for branch_id in branch_ids:
            user_data = {
                "email": f"test_{branch_id}@example.com",
                "password": "password123",
                "role": "user",
                "branch_id": branch_id
            }
            
            user = UserCreate(**user_data)
            assert user.branch_id == branch_id
    
    def test_user_create_negative_branch_id(self):
        """Test user creation with negative branch ID"""
        user_data = {
            "email": "test@example.com",
            "password": "password123",
            "role": "user",
            "branch_id": -1
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)
        
        assert "branch_id" in str(exc_info.value)
    
    def test_user_create_zero_branch_id(self):
        """Test user creation with zero branch ID"""
        user_data = {
            "email": "test@example.com",
            "password": "password123",
            "role": "user",
            "branch_id": 0
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)
        
        assert "branch_id" in str(exc_info.value)
    
    def test_user_create_long_email(self):
        """Test user creation with very long email"""
        long_email = "a" * 100 + "@example.com"
        
        user_data = {
            "email": long_email,
            "password": "password123",
            "role": "user",
            "branch_id": 1
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)
        
        assert "email" in str(exc_info.value)
    
    def test_user_create_long_password(self):
        """Test user creation with very long password"""
        long_password = "a" * 1000
        
        user_data = {
            "email": "test@example.com",
            "password": long_password,
            "role": "user",
            "branch_id": 1
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)
        
        assert "password" in str(exc_info.value)


class TestUserUpdate:
    """Test UserUpdate schema validation"""
    
    def test_user_update_all_fields(self):
        """Test user update with all fields"""
        update_data = {
            "email": "updated@example.com",
            "password": "newpassword123",
            "role": "admin",
            "branch_id": 2,
            "is_active": False
        }
        
        user_update = UserUpdate(**update_data)
        
        assert user_update.email == "updated@example.com"
        assert user_update.password == "newpassword123"
        assert user_update.role == "admin"
        assert user_update.branch_id == 2
        assert user_update.is_active is False
    
    def test_user_update_partial(self):
        """Test user update with only some fields"""
        update_data = {
            "email": "updated@example.com",
            "role": "admin"
        }
        
        user_update = UserUpdate(**update_data)
        
        assert user_update.email == "updated@example.com"
        assert user_update.role == "admin"
        assert user_update.password is None
        assert user_update.branch_id is None
        assert user_update.is_active is None
    
    def test_user_update_empty(self):
        """Test user update with no fields"""
        user_update = UserUpdate()
        
        assert user_update.email is None
        assert user_update.password is None
        assert user_update.role is None
        assert user_update.branch_id is None
        assert user_update.is_active is None
    
    def test_user_update_invalid_email(self):
        """Test user update with invalid email"""
        update_data = {
            "email": "invalid-email"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserUpdate(**update_data)
        
        assert "email" in str(exc_info.value)


class TestUserResponse:
    """Test UserResponse schema validation"""
    
    def test_user_response_valid(self):
        """Test valid user response data"""
        user_data = {
            "id": 1,
            "email": "test@example.com",
            "role": "user",
            "branch_id": 1,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        user = UserResponse(**user_data)
        
        assert user.id == 1
        assert user.email == "test@example.com"
        assert user.role == "user"
        assert user.branch_id == 1
        assert user.is_active is True
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)
    
    def test_user_response_missing_id(self):
        """Test user response with missing ID"""
        user_data = {
            "email": "test@example.com",
            "role": "user",
            "branch_id": 1,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserResponse(**user_data)
        
        assert "id" in str(exc_info.value)
    
    def test_user_response_negative_id(self):
        """Test user response with negative ID"""
        user_data = {
            "id": -1,
            "email": "test@example.com",
            "role": "user",
            "branch_id": 1,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserResponse(**user_data)
        
        assert "id" in str(exc_info.value)


class TestUserLogin:
    """Test UserLogin schema validation"""
    
    def test_user_login_valid(self):
        """Test valid user login data"""
        login_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        
        login = UserLogin(**login_data)
        
        assert login.email == "test@example.com"
        assert login.password == "password123"
    
    def test_user_login_missing_email(self):
        """Test user login with missing email"""
        login_data = {
            "password": "password123"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserLogin(**login_data)
        
        assert "email" in str(exc_info.value)
    
    def test_user_login_missing_password(self):
        """Test user login with missing password"""
        login_data = {
            "email": "test@example.com"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserLogin(**login_data)
        
        assert "password" in str(exc_info.value)
    
    def test_user_login_invalid_email(self):
        """Test user login with invalid email"""
        login_data = {
            "email": "invalid-email",
            "password": "password123"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserLogin(**login_data)
        
        assert "email" in str(exc_info.value)


class TestToken:
    """Test Token schema validation"""
    
    def test_token_valid(self):
        """Test valid token data"""
        token_data = {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer"
        }
        
        token = Token(**token_data)
        
        assert token.access_token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        assert token.token_type == "bearer"
    
    def test_token_missing_access_token(self):
        """Test token with missing access_token"""
        token_data = {
            "token_type": "bearer"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            Token(**token_data)
        
        assert "access_token" in str(exc_info.value)
    
    def test_token_missing_token_type(self):
        """Test token with missing token_type"""
        token_data = {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        }
        
        with pytest.raises(ValidationError) as exc_info:
            Token(**token_data)
        
        assert "token_type" in str(exc_info.value)
    
    def test_token_empty_access_token(self):
        """Test token with empty access_token"""
        token_data = {
            "access_token": "",
            "token_type": "bearer"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            Token(**token_data)
        
        assert "access_token" in str(exc_info.value)


class TestTokenData:
    """Test TokenData schema validation"""
    
    def test_token_data_valid(self):
        """Test valid token data"""
        token_data = {
            "sub": "test@example.com"
        }
        
        token = TokenData(**token_data)
        
        assert token.sub == "test@example.com"
    
    def test_token_data_missing_sub(self):
        """Test token data with missing sub"""
        token_data = {}
        
        with pytest.raises(ValidationError) as exc_info:
            TokenData(**token_data)
        
        assert "sub" in str(exc_info.value)
    
    def test_token_data_empty_sub(self):
        """Test token data with empty sub"""
        token_data = {
            "sub": ""
        }
        
        with pytest.raises(ValidationError) as exc_info:
            TokenData(**token_data)
        
        assert "sub" in str(exc_info.value)
    
    def test_token_data_with_optional_fields(self):
        """Test token data with optional fields"""
        token_data = {
            "sub": "test@example.com",
            "role": "admin",
            "branch_id": 1
        }
        
        token = TokenData(**token_data)
        
        assert token.sub == "test@example.com"
        assert token.role == "admin"
        assert token.branch_id == 1


class TestSchemaEdgeCases:
    """Test edge cases and special scenarios"""
    
    def test_user_create_unicode_email(self):
        """Test user creation with unicode email"""
        user_data = {
            "email": "тест@example.com",
            "password": "password123",
            "role": "user",
            "branch_id": 1
        }
        
        user = UserCreate(**user_data)
        assert user.email == "тест@example.com"
    
    def test_user_create_special_characters_password(self):
        """Test user creation with special characters in password"""
        user_data = {
            "email": "test@example.com",
            "password": "!@#$%^&*()_+-=[]{}|;':\",./<>?",
            "role": "user",
            "branch_id": 1
        }
        
        user = UserCreate(**user_data)
        assert user.password == "!@#$%^&*()_+-=[]{}|;':\",./<>?"
    
    def test_user_create_unicode_password(self):
        """Test user creation with unicode password"""
        user_data = {
            "email": "test@example.com",
            "password": "пароль123🔐",
            "role": "user",
            "branch_id": 1
        }
        
        user = UserCreate(**user_data)
        assert user.password == "пароль123🔐"
    
    def test_user_response_large_id(self):
        """Test user response with large ID"""
        user_data = {
            "id": 999999999,
            "email": "test@example.com",
            "role": "user",
            "branch_id": 1,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        user = UserResponse(**user_data)
        assert user.id == 999999999
    
    def test_user_create_large_branch_id(self):
        """Test user creation with large branch ID"""
        user_data = {
            "email": "test@example.com",
            "password": "password123",
            "role": "user",
            "branch_id": 999999
        }
        
        user = UserCreate(**user_data)
        assert user.branch_id == 999999
