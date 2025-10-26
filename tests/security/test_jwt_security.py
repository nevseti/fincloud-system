"""
Security tests for JWT token handling
"""
import pytest
import jwt
from datetime import datetime, timedelta
from app.auth_utils import create_access_token, verify_token
from app.main import app
from fastapi.testclient import TestClient


class TestJWTSecurity:
    """Test JWT security features"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_token_expiration(self):
        """Test that tokens expire correctly"""
        # Create token that expires immediately
        data = {"sub": "test@example.com"}
        token = create_access_token(data, expires_delta=timedelta(seconds=-1))
        
        # Token should be invalid due to expiration
        payload = verify_token(token)
        assert payload is None
    
    def test_token_tampering(self):
        """Test that tampered tokens are rejected"""
        # Create valid token
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        
        # Tamper with token
        tampered_token = token[:-5] + "XXXXX"
        
        # Tampered token should be invalid
        payload = verify_token(tampered_token)
        assert payload is None
    
    def test_token_without_signature(self):
        """Test token without signature"""
        # Create token without signature
        header = jwt.encode({"typ": "JWT", "alg": "HS256"}, "", algorithm="none")
        payload = jwt.encode({"sub": "test@example.com", "exp": datetime.utcnow() + timedelta(hours=1)}, "", algorithm="none")
        token_without_sig = f"{header}.{payload}."
        
        # Token without signature should be invalid
        result = verify_token(token_without_sig)
        assert result is None
    
    def test_token_with_wrong_algorithm(self):
        """Test token with wrong algorithm"""
        # Create token with wrong algorithm
        wrong_token = jwt.encode(
            {"sub": "test@example.com", "exp": datetime.utcnow() + timedelta(hours=1)},
            "wrong_secret",
            algorithm="HS256"
        )
        
        # Token with wrong secret should be invalid
        payload = verify_token(wrong_token)
        assert payload is None
    
    def test_token_injection_attempts(self):
        """Test various token injection attempts"""
        malicious_tokens = [
            "'; DROP TABLE users; --",
            "<script>alert('xss')</script>",
            "../../etc/passwd",
            "null",
            "undefined",
            "true",
            "false",
            "0",
            "1",
            "{}",
            "[]",
            "Bearer ",
            "Basic ",
            "admin",
            "root",
            "test",
            "token",
            "jwt",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",  # Example JWT
        ]
        
        for malicious_token in malicious_tokens:
            payload = verify_token(malicious_token)
            assert payload is None, f"Malicious token should be rejected: {malicious_token}"
    
    def test_token_size_limits(self):
        """Test token size limits"""
        # Create very large token
        large_data = {"sub": "a" * 10000}  # Very large subject
        large_token = create_access_token(large_data)
        
        # Should still work (JWT handles large payloads)
        payload = verify_token(large_token)
        assert payload is not None
        assert payload["sub"] == "a" * 10000
    
    def test_token_with_special_characters(self):
        """Test token with special characters in payload"""
        special_data = {
            "sub": "user+test@example.com",
            "role": "admin",
            "branch_id": 1,
            "special": "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        }
        
        token = create_access_token(special_data)
        payload = verify_token(token)
        
        assert payload is not None
        assert payload["sub"] == "user+test@example.com"
        assert payload["role"] == "admin"
        assert payload["branch_id"] == 1
        assert payload["special"] == "!@#$%^&*()_+-=[]{}|;':\",./<>?"
    
    def test_token_unicode_handling(self):
        """Test token with unicode characters"""
        unicode_data = {
            "sub": "пользователь@example.com",
            "role": "администратор",
            "branch_id": 1
        }
        
        token = create_access_token(unicode_data)
        payload = verify_token(token)
        
        assert payload is not None
        assert payload["sub"] == "пользователь@example.com"
        assert payload["role"] == "администратор"
    
    def test_token_numeric_values(self):
        """Test token with numeric values"""
        numeric_data = {
            "sub": "test@example.com",
            "user_id": 12345,
            "branch_id": 1,
            "permissions": [1, 2, 3, 4, 5]
        }
        
        token = create_access_token(numeric_data)
        payload = verify_token(token)
        
        assert payload is not None
        assert payload["user_id"] == 12345
        assert payload["branch_id"] == 1
        assert payload["permissions"] == [1, 2, 3, 4, 5]
    
    def test_token_boolean_values(self):
        """Test token with boolean values"""
        boolean_data = {
            "sub": "test@example.com",
            "is_admin": True,
            "is_active": False,
            "has_permissions": True
        }
        
        token = create_access_token(boolean_data)
        payload = verify_token(token)
        
        assert payload is not None
        assert payload["is_admin"] is True
        assert payload["is_active"] is False
        assert payload["has_permissions"] is True
    
    def test_token_nested_objects(self):
        """Test token with nested objects"""
        nested_data = {
            "sub": "test@example.com",
            "user_info": {
                "name": "John Doe",
                "age": 30,
                "address": {
                    "street": "123 Main St",
                    "city": "New York"
                }
            }
        }
        
        token = create_access_token(nested_data)
        payload = verify_token(token)
        
        assert payload is not None
        assert payload["user_info"]["name"] == "John Doe"
        assert payload["user_info"]["age"] == 30
        assert payload["user_info"]["address"]["street"] == "123 Main St"
        assert payload["user_info"]["address"]["city"] == "New York"
    
    def test_token_array_values(self):
        """Test token with array values"""
        array_data = {
            "sub": "test@example.com",
            "roles": ["user", "admin", "manager"],
            "permissions": ["read", "write", "delete"],
            "branch_ids": [1, 2, 3]
        }
        
        token = create_access_token(array_data)
        payload = verify_token(token)
        
        assert payload is not None
        assert payload["roles"] == ["user", "admin", "manager"]
        assert payload["permissions"] == ["read", "write", "delete"]
        assert payload["branch_ids"] == [1, 2, 3]
    
    def test_token_empty_values(self):
        """Test token with empty values"""
        empty_data = {
            "sub": "",
            "role": None,
            "branch_id": 0
        }
        
        token = create_access_token(empty_data)
        payload = verify_token(token)
        
        assert payload is not None
        assert payload["sub"] == ""
        assert payload["role"] is None
        assert payload["branch_id"] == 0
    
    def test_token_very_long_expiration(self):
        """Test token with very long expiration"""
        # Create token that expires in 100 years
        data = {"sub": "test@example.com"}
        token = create_access_token(data, expires_delta=timedelta(days=36500))
        
        # Token should be valid
        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == "test@example.com"
    
    def test_token_negative_expiration(self):
        """Test token with negative expiration"""
        # Create token that expired 100 years ago
        data = {"sub": "test@example.com"}
        token = create_access_token(data, expires_delta=timedelta(days=-36500))
        
        # Token should be invalid
        payload = verify_token(token)
        assert payload is None
    
    def test_token_multiple_claims(self):
        """Test token with multiple claims"""
        claims_data = {
            "sub": "test@example.com",
            "iss": "fincloud-auth",
            "aud": "fincloud-app",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=1),
            "nbf": datetime.utcnow(),
            "jti": "unique-token-id",
            "role": "admin",
            "branch_id": 1,
            "permissions": ["read", "write", "delete"]
        }
        
        token = create_access_token(claims_data)
        payload = verify_token(token)
        
        assert payload is not None
        assert payload["sub"] == "test@example.com"
        assert payload["role"] == "admin"
        assert payload["branch_id"] == 1
        assert payload["permissions"] == ["read", "write", "delete"]
    
    def test_token_case_sensitivity(self):
        """Test token case sensitivity"""
        data = {"sub": "Test@Example.COM"}
        token = create_access_token(data)
        payload = verify_token(token)
        
        assert payload is not None
        assert payload["sub"] == "Test@Example.COM"
    
    def test_token_whitespace_handling(self):
        """Test token whitespace handling"""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        
        # Test with leading/trailing whitespace
        whitespace_tokens = [
            f" {token}",
            f"{token} ",
            f" {token} ",
            f"\t{token}",
            f"{token}\t",
            f"\n{token}",
            f"{token}\n"
        ]
        
        for whitespace_token in whitespace_tokens:
            payload = verify_token(whitespace_token)
            assert payload is None, "Tokens with whitespace should be rejected"
    
    def test_token_format_validation(self):
        """Test token format validation"""
        invalid_formats = [
            "not-a-jwt-token",
            "header.payload",  # Missing signature
            "header",  # Only header
            "header.payload.signature.extra",  # Too many parts
            "header.payload.signature.extra.more",  # Even more parts
            "",  # Empty string
            "Bearer token",  # With Bearer prefix
            "Basic token",  # With Basic prefix
        ]
        
        for invalid_format in invalid_formats:
            payload = verify_token(invalid_format)
            assert payload is None, f"Invalid format should be rejected: {invalid_format}"
