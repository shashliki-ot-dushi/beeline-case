from common.database.base import engine, Base

from .user import User
from .project import Project

Base.metadata.create_all(bind=engine)