from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship

from common.database.base import Base


class Project(Base):
    __tablename__ = "projects"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    owner_id = Column(String, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="projects")