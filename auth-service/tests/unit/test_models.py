"""
Unit tests for models.py - testing database models
"""
import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import User, Base


class TestUserModel:
    """Test User model functionality"""
    
    @pytest.fixture
    def db_session(self):
        """Create in-memory SQLite database for testing"""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = SessionLocal()
        yield session
        session.close()
    
    def test_user_creation(self, db_session):
        """Test basic user creation"""
        user = User(
            email="test@example.com",
            hashed_password="hashed_password_here",
            role="user",
            branch_id=1
        )
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.hashed_password == "hashed_password_here"
        assert user.role == "user"
        assert user.branch_id == 1
        assert user.is_active is True  # Default value
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)
    
    def test_user_creation_with_custom_values(self, db_session):
        """Test user creation with custom values"""
        user = User(
            email="admin@example.com",
            hashed_password="admin_hash",
            role="admin",
            branch_id=2,
            is_active=False
        )
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        assert user.email == "admin@example.com"
        assert user.role == "admin"
        assert user.branch_id == 2
        assert user.is_active is False
    
    def test_user_email_uniqueness(self, db_session):
        """Test that email must be unique"""
        user1 = User(
            email="test@example.com",
            hashed_password="hash1",
            role="user",
            branch_id=1
        )
        
        user2 = User(
            email="test@example.com",  # Same email
            hashed_password="hash2",
            role="user",
            branch_id=1
        )
        
        db_session.add(user1)
        db_session.commit()
        
        db_session.add(user2)
        
        # Should raise integrity error
        with pytest.raises(Exception):  # SQLAlchemy will raise an exception
            db_session.commit()
    
    def test_user_required_fields(self, db_session):
        """Test that required fields are enforced"""
        # Test missing email
        with pytest.raises(Exception):
            user = User(
                hashed_password="hash",
                role="user",
                branch_id=1
            )
            db_session.add(user)
            db_session.commit()
    
    def test_user_string_representation(self, db_session):
        """Test user string representation"""
        user = User(
            email="test@example.com",
            hashed_password="hash",
            role="user",
            branch_id=1
        )
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Test that we can convert to string (for debugging)
        user_str = str(user)
        assert "test@example.com" in user_str
    
    def test_user_timestamps(self, db_session):
        """Test that timestamps are automatically set"""
        user = User(
            email="test@example.com",
            hashed_password="hash",
            role="user",
            branch_id=1
        )
        
        before_creation = datetime.utcnow()
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        after_creation = datetime.utcnow()
        
        assert before_creation <= user.created_at <= after_creation
        assert before_creation <= user.updated_at <= after_creation
    
    def test_user_update_timestamp(self, db_session):
        """Test that updated_at changes when user is modified"""
        user = User(
            email="test@example.com",
            hashed_password="hash",
            role="user",
            branch_id=1
        )
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        original_updated_at = user.updated_at
        
        # Update user
        user.role = "admin"
        db_session.commit()
        db_session.refresh(user)
        
        assert user.updated_at > original_updated_at
    
    def test_user_different_roles(self, db_session):
        """Test users with different roles"""
        roles = ["user", "admin", "manager", "system_admin"]
        
        for i, role in enumerate(roles):
            user = User(
                email=f"{role}@example.com",
                hashed_password=f"hash_{i}",
                role=role,
                branch_id=1
            )
            db_session.add(user)
        
        db_session.commit()
        
        # Verify all users were created
        users = db_session.query(User).all()
        assert len(users) == len(roles)
        
        for user in users:
            assert user.role in roles
    
    def test_user_different_branches(self, db_session):
        """Test users with different branch IDs"""
        branch_ids = [1, 2, 3, 10, 100]
        
        for i, branch_id in enumerate(branch_ids):
            user = User(
                email=f"user{i}@example.com",
                hashed_password=f"hash_{i}",
                role="user",
                branch_id=branch_id
            )
            db_session.add(user)
        
        db_session.commit()
        
        # Verify all users were created
        users = db_session.query(User).all()
        assert len(users) == len(branch_ids)
        
        for user in users:
            assert user.branch_id in branch_ids
    
    def test_user_query_by_email(self, db_session):
        """Test querying user by email"""
        user = User(
            email="test@example.com",
            hashed_password="hash",
            role="user",
            branch_id=1
        )
        
        db_session.add(user)
        db_session.commit()
        
        # Query by email
        found_user = db_session.query(User).filter(User.email == "test@example.com").first()
        
        assert found_user is not None
        assert found_user.email == "test@example.com"
    
    def test_user_query_by_role(self, db_session):
        """Test querying users by role"""
        # Create users with different roles
        users_data = [
            ("user1@example.com", "user"),
            ("admin1@example.com", "admin"),
            ("user2@example.com", "user"),
            ("manager1@example.com", "manager")
        ]
        
        for email, role in users_data:
            user = User(
                email=email,
                hashed_password="hash",
                role=role,
                branch_id=1
            )
            db_session.add(user)
        
        db_session.commit()
        
        # Query users by role
        regular_users = db_session.query(User).filter(User.role == "user").all()
        admin_users = db_session.query(User).filter(User.role == "admin").all()
        
        assert len(regular_users) == 2
        assert len(admin_users) == 1
        
        for user in regular_users:
            assert user.role == "user"
        
        for user in admin_users:
            assert user.role == "admin"
    
    def test_user_query_by_branch(self, db_session):
        """Test querying users by branch ID"""
        # Create users in different branches
        users_data = [
            ("user1@example.com", 1),
            ("user2@example.com", 1),
            ("user3@example.com", 2),
            ("user4@example.com", 3)
        ]
        
        for email, branch_id in users_data:
            user = User(
                email=email,
                hashed_password="hash",
                role="user",
                branch_id=branch_id
            )
            db_session.add(user)
        
        db_session.commit()
        
        # Query users by branch
        branch_1_users = db_session.query(User).filter(User.branch_id == 1).all()
        branch_2_users = db_session.query(User).filter(User.branch_id == 2).all()
        
        assert len(branch_1_users) == 2
        assert len(branch_2_users) == 1
        
        for user in branch_1_users:
            assert user.branch_id == 1
        
        for user in branch_2_users:
            assert user.branch_id == 2
    
    def test_user_query_active_only(self, db_session):
        """Test querying only active users"""
        # Create active and inactive users
        users_data = [
            ("active1@example.com", True),
            ("inactive1@example.com", False),
            ("active2@example.com", True),
            ("inactive2@example.com", False)
        ]
        
        for email, is_active in users_data:
            user = User(
                email=email,
                hashed_password="hash",
                role="user",
                branch_id=1,
                is_active=is_active
            )
            db_session.add(user)
        
        db_session.commit()
        
        # Query only active users
        active_users = db_session.query(User).filter(User.is_active == True).all()
        inactive_users = db_session.query(User).filter(User.is_active == False).all()
        
        assert len(active_users) == 2
        assert len(inactive_users) == 2
        
        for user in active_users:
            assert user.is_active is True
        
        for user in inactive_users:
            assert user.is_active is False
