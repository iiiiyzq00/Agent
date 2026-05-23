"""项目和清单相关模型"""
from sqlalchemy import Column, String, Text, Date, Integer, Float, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.database import Base

class Project(Base):
    """项目表"""
    __tablename__ = "projects"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    project_type = Column(String(20), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    status = Column(String(20), default="planning", index=True)
    requirements = Column(JSON, default=dict)
    source_address = Column(String(500))
    target_address = Column(String(500))
    moving_date = Column(Date)
    mover_count = Column(Integer, default=2)
    house_type = Column(String(50))
    house_area = Column(Float)
    current_state = Column(String(50))
    style = Column(String(50))
    total_budget = Column(Float, default=0)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship("User", back_populates="projects")
    checklists = relationship("Checklist", back_populates="project", cascade="all, delete-orphan")
    budgets = relationship("Budget", back_populates="project", cascade="all, delete-orphan")
    phases = relationship("Phase", back_populates="project", cascade="all, delete-orphan")

class Checklist(Base):
    """清单表"""
    __tablename__ = "checklists"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)
    checklist_type = Column(String(30), nullable=False)
    category = Column(String(50))
    name = Column(String(200), nullable=False)
    description = Column(Text)
    total_items = Column(Integer, default=0)
    completed_items = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    project = relationship("Project", back_populates="checklists")
    items = relationship("ChecklistItem", back_populates="checklist", cascade="all, delete-orphan")

    @property
    def progress(self):
        if self.total_items == 0:
            return 0
        return round((self.completed_items / self.total_items) * 100, 1)

class ChecklistItem(Base):
    """清单项表"""
    __tablename__ = "checklist_items"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    checklist_id = Column(UUID(as_uuid=True), ForeignKey("checklists.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    quantity = Column(Integer, default=1)
    unit = Column(String(20))
    room = Column(String(100))
    category = Column(String(50))
    pack_order = Column(Integer, default=0)
    box_number = Column(String(50))
    label = Column(String(200))
    priority = Column(String(20), default="normal")
    is_fragile = Column(Boolean, default=False)
    is_valuable = Column(Boolean, default=False)
    is_packed = Column(Boolean, default=False, index=True)
    is_unpacked = Column(Boolean, default=False, index=True)
    packed_at = Column(DateTime)
    unpacked_at = Column(DateTime)
    estimated_cost = Column(Float, default=0)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    checklist = relationship("Checklist", back_populates="items")

class Budget(Base):
    """预算表"""
    __tablename__ = "budgets"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)
    category = Column(String(50), nullable=False)
    item_name = Column(String(200), nullable=False)
    specifications = Column(Text)
    unit = Column(String(20))
    quantity = Column(Float, default=1)
    unit_price = Column(Float, default=0)
    planned_amount = Column(Float, default=0)
    actual_amount = Column(Float, default=0)
    supplier = Column(String(200))
    purchase_url = Column(String(500))
    purchase_date = Column(Date)
    status = Column(String(20), default="pending")
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    project = relationship("Project", back_populates="budgets")

    @property
    def total_price(self):
        return self.quantity * self.unit_price

class Phase(Base):
    """施工阶段表"""
    __tablename__ = "phases"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    order_index = Column(Integer, nullable=False, index=True)
    description = Column(Text)
    start_date = Column(Date)
    end_date = Column(Date)
    estimated_days = Column(Integer, default=0)
    status = Column(String(20), default="pending")
    progress = Column(Integer, default=0)
    tasks = Column(JSON, default=list)
    checkpoints = Column(JSON, default=list)
    is_accepted = Column(Boolean, default=False)
    budget = Column(Float, default=0)
    actual_cost = Column(Float, default=0)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    project = relationship("Project", back_populates="phases")

class Conversation(Base):
    """对话历史表"""
    __tablename__ = "conversations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    metadata = Column(JSON, default=dict)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    session_id = Column(String(100), index=True)
    tokens_used = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    user = relationship("User", back_populates="conversations")
