"""
Database tests for Auth Service
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import User, Base
from app.database import get_db
from app.main import app
from fastapi.testclient import TestClient


class TestAuthDatabase:
    """Test Auth Service database operations"""
    
    @pytest.fixture(scope="class")
    def test_db_engine(self):
        """Create test database engine"""
        engine = create_engine("sqlite:///./test_auth.db")
        Base.metadata.create_all(engine)
        return engine
    
    @pytest.fixture
    def test_db_session(self, test_db_engine):
        """Create test database session"""
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db_engine)
        session = SessionLocal()
        yield session
        session.close()
    
    @pytest.fixture
    def client(self, test_db_session):
        """Create test client with test database"""
        def override_get_db():
            try:
                yield test_db_session
            finally:
                pass
        
        app.dependency_overrides[get_db] = override_get_db
        client = TestClient(app)
        yield client
        app.dependency_overrides.clear()
    
    def test_database_connection(self, test_db_session):
        """Test database connection"""
        # Test basic database connection
        result = test_db_session.execute("SELECT 1").scalar()
        assert result == 1
    
    def test_user_table_creation(self, test_db_session):
        """Test user table creation"""
        # Check if user table exists
        result = test_db_session.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'").fetchone()
        assert result is not None
        assert result[0] == "users"
    
    def test_user_crud_operations(self, test_db_session):
        """Test user CRUD operations"""
        # Create user
        user = User(
            email="test@example.com",
            hashed_password="hashed_password",
            role="user",
            branch_id=1
        )
        
        test_db_session.add(user)
        test_db_session.commit()
        test_db_session.refresh(user)
        
        assert user.id is not None
        assert user.email == "test@example.com"
        
        # Read user
        found_user = test_db_session.query(User).filter(User.email == "test@example.com").first()
        assert found_user is not None
        assert found_user.email == "test@example.com"
        assert found_user.role == "user"
        assert found_user.branch_id == 1
        
        # Update user
        found_user.role = "admin"
        found_user.branch_id = 2
        test_db_session.commit()
        test_db_session.refresh(found_user)
        
        assert found_user.role == "admin"
        assert found_user.branch_id == 2
        
        # Delete user
        test_db_session.delete(found_user)
        test_db_session.commit()
        
        # Verify deletion
        deleted_user = test_db_session.query(User).filter(User.email == "test@example.com").first()
        assert deleted_user is None
    
    def test_user_email_uniqueness(self, test_db_session):
        """Test user email uniqueness constraint"""
        # Create first user
        user1 = User(
            email="unique@example.com",
            hashed_password="hash1",
            role="user",
            branch_id=1
        )
        
        test_db_session.add(user1)
        test_db_session.commit()
        
        # Try to create second user with same email
        user2 = User(
            email="unique@example.com",
            hashed_password="hash2",
            role="user",
            branch_id=1
        )
        
        test_db_session.add(user2)
        
        # Should raise integrity error
        with pytest.raises(Exception):
            test_db_session.commit()
    
    def test_user_required_fields(self, test_db_session):
        """Test user required fields"""
        # Test missing email
        with pytest.raises(Exception):
            user = User(
                hashed_password="hash",
                role="user",
                branch_id=1
            )
            test_db_session.add(user)
            test_db_session.commit()
    
    def test_user_default_values(self, test_db_session):
        """Test user default values"""
        user = User(
            email="default@example.com",
            hashed_password="hash",
            role="user",
            branch_id=1
        )
        
        test_db_session.add(user)
        test_db_session.commit()
        test_db_session.refresh(user)
        
        assert user.is_active is True  # Default value
    
    def test_user_timestamps(self, test_db_session):
        """Test user timestamp fields"""
        from datetime import datetime
        
        user = User(
            email="timestamp@example.com",
            hashed_password="hash",
            role="user",
            branch_id=1
        )
        
        before_creation = datetime.utcnow()
        test_db_session.add(user)
        test_db_session.commit()
        test_db_session.refresh(user)
        after_creation = datetime.utcnow()
        
        assert before_creation <= user.created_at <= after_creation
        assert before_creation <= user.updated_at <= after_creation
    
    def test_user_query_operations(self, test_db_session):
        """Test user query operations"""
        # Create test users
        users_data = [
            ("user1@example.com", "user", 1),
            ("admin1@example.com", "admin", 1),
            ("user2@example.com", "user", 2),
            ("manager1@example.com", "manager", 2)
        ]
        
        for email, role, branch_id in users_data:
            user = User(
                email=email,
                hashed_password="hash",
                role=role,
                branch_id=branch_id
            )
            test_db_session.add(user)
        
        test_db_session.commit()
        
        # Test query by role
        regular_users = test_db_session.query(User).filter(User.role == "user").all()
        assert len(regular_users) == 2
        
        admin_users = test_db_session.query(User).filter(User.role == "admin").all()
        assert len(admin_users) == 1
        
        # Test query by branch
        branch_1_users = test_db_session.query(User).filter(User.branch_id == 1).all()
        assert len(branch_1_users) == 2
        
        branch_2_users = test_db_session.query(User).filter(User.branch_id == 2).all()
        assert len(branch_2_users) == 2
        
        # Test query by email
        specific_user = test_db_session.query(User).filter(User.email == "admin1@example.com").first()
        assert specific_user is not None
        assert specific_user.role == "admin"
    
    def test_user_pagination(self, test_db_session):
        """Test user pagination"""
        # Create many users
        for i in range(25):
            user = User(
                email=f"user{i}@example.com",
                hashed_password="hash",
                role="user",
                branch_id=1
            )
            test_db_session.add(user)
        
        test_db_session.commit()
        
        # Test pagination
        page_1 = test_db_session.query(User).offset(0).limit(10).all()
        assert len(page_1) == 10
        
        page_2 = test_db_session.query(User).offset(10).limit(10).all()
        assert len(page_2) == 10
        
        page_3 = test_db_session.query(User).offset(20).limit(10).all()
        assert len(page_3) == 5  # Only 5 users left
        
        # Test total count
        total_count = test_db_session.query(User).count()
        assert total_count == 25
    
    def test_user_ordering(self, test_db_session):
        """Test user ordering"""
        # Create users with different emails
        emails = ["z@example.com", "a@example.com", "m@example.com"]
        
        for email in emails:
            user = User(
                email=email,
                hashed_password="hash",
                role="user",
                branch_id=1
            )
            test_db_session.add(user)
        
        test_db_session.commit()
        
        # Test ordering by email
        users_asc = test_db_session.query(User).order_by(User.email.asc()).all()
        assert users_asc[0].email == "a@example.com"
        assert users_asc[1].email == "m@example.com"
        assert users_asc[2].email == "z@example.com"
        
        users_desc = test_db_session.query(User).order_by(User.email.desc()).all()
        assert users_desc[0].email == "z@example.com"
        assert users_desc[1].email == "m@example.com"
        assert users_desc[2].email == "a@example.com"
    
    def test_user_filtering(self, test_db_session):
        """Test user filtering"""
        # Create users with different attributes
        users_data = [
            ("active@example.com", "user", 1, True),
            ("inactive@example.com", "user", 1, False),
            ("admin@example.com", "admin", 2, True),
            ("manager@example.com", "manager", 2, False)
        ]
        
        for email, role, branch_id, is_active in users_data:
            user = User(
                email=email,
                hashed_password="hash",
                role=role,
                branch_id=branch_id,
                is_active=is_active
            )
            test_db_session.add(user)
        
        test_db_session.commit()
        
        # Test filtering by active status
        active_users = test_db_session.query(User).filter(User.is_active == True).all()
        assert len(active_users) == 2
        
        inactive_users = test_db_session.query(User).filter(User.is_active == False).all()
        assert len(inactive_users) == 2
        
        # Test complex filtering
        active_admins = test_db_session.query(User).filter(
            User.role == "admin",
            User.is_active == True
        ).all()
        assert len(active_admins) == 1
        assert active_admins[0].email == "admin@example.com"
    
    def test_user_relationships(self, test_db_session):
        """Test user relationships (if any)"""
        # For now, User model doesn't have relationships
        # This test is a placeholder for future relationship tests
        
        user = User(
            email="relationship@example.com",
            hashed_password="hash",
            role="user",
            branch_id=1
        )
        
        test_db_session.add(user)
        test_db_session.commit()
        test_db_session.refresh(user)
        
        # Basic test that user can be created and retrieved
        assert user.id is not None
        assert user.email == "relationship@example.com"
    
    def test_database_transactions(self, test_db_session):
        """Test database transactions"""
        # Test successful transaction
        user1 = User(
            email="transaction1@example.com",
            hashed_password="hash",
            role="user",
            branch_id=1
        )
        
        user2 = User(
            email="transaction2@example.com",
            hashed_password="hash",
            role="user",
            branch_id=1
        )
        
        test_db_session.add(user1)
        test_db_session.add(user2)
        test_db_session.commit()
        
        # Both users should be created
        assert test_db_session.query(User).filter(User.email == "transaction1@example.com").first() is not None
        assert test_db_session.query(User).filter(User.email == "transaction2@example.com").first() is not None
        
        # Test rollback
        user3 = User(
            email="transaction3@example.com",
            hashed_password="hash",
            role="user",
            branch_id=1
        )
        
        test_db_session.add(user3)
        test_db_session.rollback()
        
        # User3 should not be created
        assert test_db_session.query(User).filter(User.email == "transaction3@example.com").first() is None
    
    def test_database_constraints(self, test_db_session):
        """Test database constraints"""
        # Test email uniqueness
        user1 = User(
            email="constraint@example.com",
            hashed_password="hash",
            role="user",
            branch_id=1
        )
        
        test_db_session.add(user1)
        test_db_session.commit()
        
        # Try to create user with same email
        user2 = User(
            email="constraint@example.com",
            hashed_password="hash2",
            role="user",
            branch_id=1
        )
        
        test_db_session.add(user2)
        
        with pytest.raises(Exception):
            test_db_session.commit()
    
    def test_database_indexes(self, test_db_session):
        """Test database indexes"""
        # This test would check if indexes are properly created
        # For SQLite, we can check the schema
        
        result = test_db_session.execute("PRAGMA index_list(users)").fetchall()
        
        # Should have at least one index (primary key)
        assert len(result) >= 1
        
        # Check if email index exists (if created)
        indexes = [row[1] for row in result]
        print(f"Available indexes: {indexes}")
    
    def test_database_cleanup(self, test_db_session):
        """Test database cleanup"""
        # Create test data
        user = User(
            email="cleanup@example.com",
            hashed_password="hash",
            role="user",
            branch_id=1
        )
        
        test_db_session.add(user)
        test_db_session.commit()
        
        # Verify user exists
        assert test_db_session.query(User).filter(User.email == "cleanup@example.com").first() is not None
        
        # Cleanup
        test_db_session.query(User).filter(User.email == "cleanup@example.com").delete()
        test_db_session.commit()
        
        # Verify cleanup
        assert test_db_session.query(User).filter(User.email == "cleanup@example.com").first() is None
