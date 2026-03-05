from .minirag_base import SQLAlchemyBase
from sqlalchemy import Column, Integer, String, func, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.orm import relationship

class Project(SQLAlchemyBase): 

    __tablename__ = "projects"
    project_id = Column(Integer, primary_key=True,autoincrement=True)
    project_uuid = Column(UUID(as_uuid=True), unique=True,nullable=False, default=uuid.uuid4)
    project_name = Column(String(255), nullable=False)
    project_description = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=func.now())

    chunks = relationship("DataChunk", back_populates="project")
    assets = relationship("Asset", back_populates="project")
    
