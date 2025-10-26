"""
Performance tests for Auth Service
"""
import pytest
import time
import asyncio
import httpx
from concurrent.futures import ThreadPoolExecutor
from app.main import app
from fastapi.testclient import TestClient


class TestAuthPerformance:
    """Test Auth Service performance"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_password_hashing_performance(self):
        """Test password hashing performance"""
        from app.auth_utils import get_password_hash, verify_password
        
        password = "test_password_123"
        
        # Test hashing performance
        start_time = time.time()
        hashed = get_password_hash(password)
        hash_time = time.time() - start_time
        
        # Test verification performance
        start_time = time.time()
        is_valid = verify_password(password, hashed)
        verify_time = time.time() - start_time
        
        assert is_valid is True
        assert hash_time < 1.0  # Should hash in less than 1 second
        assert verify_time < 1.0  # Should verify in less than 1 second
        
        print(f"Hash time: {hash_time:.4f}s, Verify time: {verify_time:.4f}s")
    
    def test_jwt_token_creation_performance(self):
        """Test JWT token creation performance"""
        from app.auth_utils import create_access_token, verify_token
        
        data = {"sub": "test@example.com", "role": "user", "branch_id": 1}
        
        # Test token creation performance
        start_time = time.time()
        token = create_access_token(data)
        create_time = time.time() - start_time
        
        # Test token verification performance
        start_time = time.time()
        payload = verify_token(token)
        verify_time = time.time() - start_time
        
        assert payload is not None
        assert payload["sub"] == "test@example.com"
        assert create_time < 0.1  # Should create token in less than 100ms
        assert verify_time < 0.1  # Should verify token in less than 100ms
        
        print(f"Token creation time: {create_time:.4f}s, Verification time: {verify_time:.4f}s")
    
    def test_concurrent_password_hashing(self):
        """Test concurrent password hashing performance"""
        from app.auth_utils import get_password_hash, verify_password
        
        def hash_password(password):
            return get_password_hash(password)
        
        def verify_password_pair(password, hashed):
            return verify_password(password, hashed)
        
        password = "test_password_123"
        num_threads = 10
        num_operations = 100
        
        # Test concurrent hashing
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(hash_password, password) for _ in range(num_operations)]
            hashes = [future.result() for future in futures]
        concurrent_hash_time = time.time() - start_time
        
        # Test concurrent verification
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(verify_password_pair, password, hashes[i]) for i in range(num_operations)]
            results = [future.result() for future in futures]
        concurrent_verify_time = time.time() - start_time
        
        # All verifications should succeed
        assert all(results)
        assert concurrent_hash_time < 10.0  # Should complete in less than 10 seconds
        assert concurrent_verify_time < 5.0  # Should complete in less than 5 seconds
        
        print(f"Concurrent hash time ({num_operations} ops): {concurrent_hash_time:.4f}s")
        print(f"Concurrent verify time ({num_operations} ops): {concurrent_verify_time:.4f}s")
    
    def test_concurrent_jwt_operations(self):
        """Test concurrent JWT operations performance"""
        from app.auth_utils import create_access_token, verify_token
        
        def create_token(data):
            return create_access_token(data)
        
        def verify_token_safe(token):
            return verify_token(token)
        
        data = {"sub": "test@example.com", "role": "user", "branch_id": 1}
        num_threads = 10
        num_operations = 100
        
        # Test concurrent token creation
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(create_token, data) for _ in range(num_operations)]
            tokens = [future.result() for future in futures]
        concurrent_create_time = time.time() - start_time
        
        # Test concurrent token verification
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(verify_token_safe, tokens[i]) for i in range(num_operations)]
            results = [future.result() for future in futures]
        concurrent_verify_time = time.time() - start_time
        
        # All verifications should succeed
        assert all(results)
        assert concurrent_create_time < 2.0  # Should complete in less than 2 seconds
        assert concurrent_verify_time < 1.0  # Should complete in less than 1 second
        
        print(f"Concurrent token creation time ({num_operations} ops): {concurrent_create_time:.4f}s")
        print(f"Concurrent token verification time ({num_operations} ops): {concurrent_verify_time:.4f}s")
    
    def test_api_endpoint_performance(self, client):
        """Test API endpoint performance"""
        # Test health endpoint performance
        start_time = time.time()
        response = client.get("/health")
        health_time = time.time() - start_time
        
        assert response.status_code == 200
        assert health_time < 0.1  # Should respond in less than 100ms
        
        print(f"Health endpoint response time: {health_time:.4f}s")
    
    def test_user_registration_performance(self, client):
        """Test user registration performance"""
        user_data = {
            "email": "perf_test@example.com",
            "password": "password123",
            "role": "user",
            "branch_id": 1
        }
        
        # Test registration performance
        start_time = time.time()
        response = client.post("/register", json=user_data)
        registration_time = time.time() - start_time
        
        assert response.status_code == 200
        assert registration_time < 2.0  # Should complete in less than 2 seconds
        
        print(f"User registration time: {registration_time:.4f}s")
    
    def test_user_login_performance(self, client):
        """Test user login performance"""
        # First register a user
        user_data = {
            "email": "login_perf@example.com",
            "password": "password123",
            "role": "user",
            "branch_id": 1
        }
        
        response = client.post("/register", json=user_data)
        assert response.status_code == 200
        
        # Test login performance
        login_data = {
            "email": "login_perf@example.com",
            "password": "password123"
        }
        
        start_time = time.time()
        response = client.post("/login", json=login_data)
        login_time = time.time() - start_time
        
        assert response.status_code == 200
        assert login_time < 1.0  # Should complete in less than 1 second
        
        print(f"User login time: {login_time:.4f}s")
    
    def test_concurrent_api_requests(self, client):
        """Test concurrent API requests performance"""
        def make_health_request():
            return client.get("/health")
        
        num_requests = 50
        num_threads = 10
        
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(make_health_request) for _ in range(num_requests)]
            responses = [future.result() for future in futures]
        concurrent_time = time.time() - start_time
        
        # All requests should succeed
        assert all(response.status_code == 200 for response in responses)
        assert concurrent_time < 5.0  # Should complete in less than 5 seconds
        
        print(f"Concurrent API requests time ({num_requests} requests): {concurrent_time:.4f}s")
    
    def test_memory_usage_during_operations(self):
        """Test memory usage during operations"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Perform many operations
        from app.auth_utils import create_access_token, verify_token
        
        tokens = []
        for i in range(1000):
            data = {"sub": f"user{i}@example.com", "role": "user", "branch_id": 1}
            token = create_access_token(data)
            tokens.append(token)
        
        # Verify all tokens
        for token in tokens:
            payload = verify_token(token)
            assert payload is not None
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable
        assert memory_increase < 100  # Should not increase by more than 100MB
        
        print(f"Memory usage increase: {memory_increase:.2f}MB")
    
    def test_large_payload_performance(self, client):
        """Test performance with large payloads"""
        # Test with large user data
        large_user_data = {
            "email": "large_user@example.com",
            "password": "a" * 1000,  # Large password
            "role": "user",
            "branch_id": 1
        }
        
        start_time = time.time()
        response = client.post("/register", json=large_user_data)
        large_registration_time = time.time() - start_time
        
        assert response.status_code == 200
        assert large_registration_time < 5.0  # Should complete in less than 5 seconds
        
        print(f"Large payload registration time: {large_registration_time:.4f}s")
    
    def test_database_connection_performance(self, client):
        """Test database connection performance"""
        # This test would require a real database connection
        # For now, we'll test the health endpoint which might use the database
        
        start_time = time.time()
        response = client.get("/health")
        db_health_time = time.time() - start_time
        
        assert response.status_code == 200
        assert db_health_time < 1.0  # Should complete in less than 1 second
        
        print(f"Database health check time: {db_health_time:.4f}s")
    
    def test_error_handling_performance(self, client):
        """Test error handling performance"""
        # Test with invalid data
        invalid_data = {
            "email": "invalid-email",
            "password": "",
            "role": "invalid_role",
            "branch_id": -1
        }
        
        start_time = time.time()
        response = client.post("/register", json=invalid_data)
        error_handling_time = time.time() - start_time
        
        assert response.status_code == 422  # Validation error
        assert error_handling_time < 0.5  # Should handle errors quickly
        
        print(f"Error handling time: {error_handling_time:.4f}s")
    
    def test_token_refresh_performance(self):
        """Test token refresh performance"""
        from app.auth_utils import create_access_token, verify_token
        
        # Create initial token
        data = {"sub": "test@example.com", "role": "user", "branch_id": 1}
        initial_token = create_access_token(data)
        
        # Simulate token refresh by creating new token
        start_time = time.time()
        new_token = create_access_token(data)
        refresh_time = time.time() - start_time
        
        # Verify new token
        payload = verify_token(new_token)
        assert payload is not None
        assert refresh_time < 0.1  # Should refresh quickly
        
        print(f"Token refresh time: {refresh_time:.4f}s")
    
    def test_bulk_operations_performance(self, client):
        """Test bulk operations performance"""
        # Register multiple users
        num_users = 20
        start_time = time.time()
        
        for i in range(num_users):
            user_data = {
                "email": f"bulk_user_{i}@example.com",
                "password": "password123",
                "role": "user",
                "branch_id": 1
            }
            response = client.post("/register", json=user_data)
            assert response.status_code == 200
        
        bulk_registration_time = time.time() - start_time
        
        # Should complete in reasonable time
        assert bulk_registration_time < 10.0  # Should complete in less than 10 seconds
        
        print(f"Bulk registration time ({num_users} users): {bulk_registration_time:.4f}s")
