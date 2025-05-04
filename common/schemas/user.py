from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from common.database.base import Base


class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True)
    session_token = Column(String, unique=True, index=True)
    projects = relationship(
        "Project",
        back_populates="owner",
        cascade="all, delete-orphan"
    )