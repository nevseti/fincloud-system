"""
Unit tests for auth_utils.py - testing each function individually
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from app.auth_utils import (
    verify_password,
    get_password_hash,
    create_access_token,
    verify_token,
    get_current_user,
    get_current_active_user
)
from app.models import User
from app.schemas import UserResponse


class TestPasswordHashing:
    """Test password hashing functions"""
    
    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = get_password_hash(password)
        
        assert verify_password(wrong_password, hashed) is False
    
    def test_verify_password_empty(self):
        """Test password verification with empty password"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert verify_password("", hashed) is False
    
    def test_get_password_hash_consistency(self):
        """Test that password hashing is consistent"""
        password = "testpassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # Hashes should be different (salt), but both should verify
        assert hash1 != hash2
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True
    
    def test_password_hash_length(self):
        """Test that password hash has reasonable length"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        # bcrypt hashes are typically 60 characters
        assert len(hashed) == 60
    
    def test_very_long_password(self):
        """Test password hashing with very long password"""
        long_password = "a" * 1000
        hashed = get_password_hash(long_password)
        
        assert verify_password(long_password, hashed) is True


class TestJWTTokenCreation:
    """Test JWT token creation and verification"""
    
    def test_create_access_token_basic(self):
        """Test basic access token creation"""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
        # JWT tokens have 3 parts separated by dots
        assert len(token.split('.')) == 3
    
    def test_create_access_token_with_expires_delta(self):
        """Test access token creation with custom expiration"""
        data = {"sub": "test@example.com"}
        expires_delta = timedelta(minutes=30)
        token = create_access_token(data, expires_delta)
        
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_access_token_different_subjects(self):
        """Test token creation for different subjects"""
        data1 = {"sub": "user1@example.com"}
        data2 = {"sub": "user2@example.com"}
        
        token1 = create_access_token(data1)
        token2 = create_access_token(data2)
        
        assert token1 != token2
    
    def test_create_access_token_with_additional_data(self):
        """Test token creation with additional data"""
        data = {
            "sub": "test@example.com",
            "role": "admin",
            "branch_id": 1
        }
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0


class TestJWTTokenVerification:
    """Test JWT token verification"""
    
    def test_verify_token_valid(self):
        """Test verification of valid token"""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        
        payload = verify_token(token)
        
        assert payload is not None
        assert payload.get("sub") == "test@example.com"
    
    def test_verify_token_invalid(self):
        """Test verification of invalid token"""
        invalid_token = "invalid.token.here"
        
        payload = verify_token(invalid_token)
        
        assert payload is None
    
    def test_verify_token_expired(self):
        """Test verification of expired token"""
        data = {"sub": "test@example.com"}
        # Create token that expires immediately
        token = create_access_token(data, expires_delta=timedelta(seconds=-1))
        
        payload = verify_token(token)
        
        assert payload is None
    
    def test_verify_token_empty(self):
        """Test verification of empty token"""
        payload = verify_token("")
        
        assert payload is None
    
    def test_verify_token_none(self):
        """Test verification of None token"""
        payload = verify_token(None)
        
        assert payload is None


class TestGetCurrentUser:
    """Test get_current_user function"""
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock database session"""
        return MagicMock()
    
    @pytest.fixture
    def mock_user(self):
        """Mock user object"""
        user = MagicMock(spec=User)
        user.id = 1
        user.email = "test@example.com"
        user.role = "user"
        user.branch_id = 1
        user.is_active = True
        return user
    
    @patch('app.auth_utils.verify_token')
    def test_get_current_user_valid_token(self, mock_verify_token, mock_db_session, mock_user):
        """Test get_current_user with valid token"""
        # Setup
        mock_verify_token.return_value = {"sub": "test@example.com"}
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user
        
        # Test
        result = get_current_user("valid_token", mock_db_session)
        
        # Assertions
        assert result == mock_user
        mock_verify_token.assert_called_once_with("valid_token")
        mock_db_session.query.assert_called_once_with(User)
    
    @patch('app.auth_utils.verify_token')
    def test_get_current_user_invalid_token(self, mock_verify_token, mock_db_session):
        """Test get_current_user with invalid token"""
        # Setup
        mock_verify_token.return_value = None
        
        # Test
        result = get_current_user("invalid_token", mock_db_session)
        
        # Assertions
        assert result is None
        mock_verify_token.assert_called_once_with("invalid_token")
        mock_db_session.query.assert_not_called()
    
    @patch('app.auth_utils.verify_token')
    def test_get_current_user_user_not_found(self, mock_verify_token, mock_db_session):
        """Test get_current_user when user not found in database"""
        # Setup
        mock_verify_token.return_value = {"sub": "nonexistent@example.com"}
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        # Test
        result = get_current_user("valid_token", mock_db_session)
        
        # Assertions
        assert result is None
        mock_verify_token.assert_called_once_with("valid_token")
        mock_db_session.query.assert_called_once_with(User)


class TestGetCurrentActiveUser:
    """Test get_current_active_user function"""
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock database session"""
        return MagicMock()
    
    @pytest.fixture
    def active_user(self):
        """Mock active user"""
        user = MagicMock(spec=User)
        user.id = 1
        user.email = "test@example.com"
        user.role = "user"
        user.branch_id = 1
        user.is_active = True
        return user
    
    @pytest.fixture
    def inactive_user(self):
        """Mock inactive user"""
        user = MagicMock(spec=User)
        user.id = 2
        user.email = "inactive@example.com"
        user.role = "user"
        user.branch_id = 1
        user.is_active = False
        return user
    
    @patch('app.auth_utils.get_current_user')
    def test_get_current_active_user_active(self, mock_get_current_user, mock_db_session, active_user):
        """Test get_current_active_user with active user"""
        # Setup
        mock_get_current_user.return_value = active_user
        
        # Test
        result = get_current_active_user("valid_token", mock_db_session)
        
        # Assertions
        assert result == active_user
        mock_get_current_user.assert_called_once_with("valid_token", mock_db_session)
    
    @patch('app.auth_utils.get_current_user')
    def test_get_current_active_user_inactive(self, mock_get_current_user, mock_db_session, inactive_user):
        """Test get_current_active_user with inactive user"""
        # Setup
        mock_get_current_user.return_value = inactive_user
        
        # Test
        result = get_current_active_user("valid_token", mock_db_session)
        
        # Assertions
        assert result is None
        mock_get_current_user.assert_called_once_with("valid_token", mock_db_session)
    
    @patch('app.auth_utils.get_current_user')
    def test_get_current_active_user_none(self, mock_get_current_user, mock_db_session):
        """Test get_current_active_user when get_current_user returns None"""
        # Setup
        mock_get_current_user.return_value = None
        
        # Test
        result = get_current_active_user("invalid_token", mock_db_session)
        
        # Assertions
        assert result is None
        mock_get_current_user.assert_called_once_with("invalid_token", mock_db_session)


class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_password_hash_special_characters(self):
        """Test password hashing with special characters"""
        password = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
    
    def test_password_hash_unicode(self):
        """Test password hashing with unicode characters"""
        password = "пароль123🔐"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
    
    def test_token_with_special_characters_in_subject(self):
        """Test token creation with special characters in subject"""
        data = {"sub": "user+test@example.com"}
        token = create_access_token(data)
        
        payload = verify_token(token)
        
        assert payload is not None
        assert payload.get("sub") == "user+test@example.com"
    
    def test_token_verification_with_whitespace(self):
        """Test token verification with whitespace"""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        
        # Test with whitespace
        payload = verify_token(f" {token} ")
        
        assert payload is None  # Should fail due to whitespace
