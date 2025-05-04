from .base import get_database_connection


def get_db():
    db = get_database_connection()
    try:
        yield db
    finally:
        db.close()