"""用户模型"""​
from sqlalchemy import Column, String, DateTime, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID​
from sqlalchemy.orm import relationship​
import uuid​
from datetime import datetime​
from app.database import Base​

class User(Base):​
    """用户表"""​
    __tablename__ = "users"​
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)​
    username = Column(String(50), unique=True, nullable=False, index=True)​
    email = Column(String(255), unique=True, nullable=False, index=True)​
    password_hash = Column(String(255), nullable=False)​
    full_name = Column(String(100))​
    phone = Column(String(20))​
    avatar_url = Column(String(500))​
    preferences = Column(JSON, default=dict)​
    is_active = Column(Boolean, default=True)​
    is_verified = Column(Boolean, default=False)​
    created_at = Column(DateTime, default=datetime.utcnow, index=True)​
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)​
    last_login = Column(DateTime)​
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")​
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")​
    
def to_dict(self):​  
    return {​
        "id": str(self.id),​
        "username": self.username,​
        "email": self.email,​
        "full_name": self.full_name,​
        "phone": self.phone,​
        "avatar_url": self.avatar_url,​
        "preferences": self.preferences,​
        "is_active": self.is_active,​
        "created_at": self.created_at.isoformat() if self.created_at else None,​
        "last_login": self.last_login.isoformat() if self.last_login else None,​
    }
