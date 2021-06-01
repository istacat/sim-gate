from datetime import datetime, timedelta

from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.hash import bcrypt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.api.models.auth import User, Token, UserCreate
from app.db import get_session
from app.db import models as db
from config import config


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/sign_in")


def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    return AuthService.validate_token(token) 


class AuthService:
    def __init__(self, session: Session = Depends(get_session)) -> None:
        self.session = session

    def register_new_user(self, user_data: UserCreate) -> Token:
        user = db.User(
            username=user_data.username,
            password_hash=self.hash_password(user_data.password)
        )
        self.session.add(user)
        self.session.commit()

        return self.create_token(user)

    def authenticate_user(self, username: str, password: str) -> Token:
        def exception():
            return HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={
                    "WWW-Authenticate": "Bearer"
                }
            )

        user = (
            self.session
            .query(db.User)
            .filter(db.User.username == username)
            .first()
        )

        if not user:
            raise exception()

        if not self.verify_password(password, user.password_hash):
            raise exception()
        
        return self.create_token(user)

    @classmethod
    def verify_password(cls, password: str, hashed_password: str) -> bool:
        return bcrypt.verify(password, hashed_password)

    @classmethod
    def hash_password(cls, password: str) -> str:
        return bcrypt.hash(password)

    @classmethod
    def validate_token(cls, token: str) -> User:
        exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

        try:
            payload = jwt.decode(
                token,
                config.JWT_SECRET,
                algorithms=[config.JWT_ALGORITHM]
            )
        except JWTError:
            raise exception from None
        
        user_data = payload.get("user")

        try:
            user = User.parse_obj(user_data)
        except ValidationError:
            raise exception from None

        return user

    @classmethod
    def create_token(cls, user: db.User) -> Token:
        user_data = User.from_orm(user)

        now = datetime.utcnow()
        payload = {
            "iat": now,
            "nbf": now,
            "exp": now + timedelta(seconds=int(config.JWT_EXP)),
            "sub": str(user_data.id),
            "user": user_data.dict()
        }
        token = jwt.encode(
            payload,
            config.JWT_SECRET,
            algorithm=config.JWT_ALGORITHM
        )
        return Token(access_token=token)

