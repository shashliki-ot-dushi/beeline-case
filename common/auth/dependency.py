from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from .policy import security

from common.database.base import Base
from common.database.dependency import get_db
from common.schemas.user import User


def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:

    token = creds.credentials
    user = db.query(User).filter(User.session_token == token).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user