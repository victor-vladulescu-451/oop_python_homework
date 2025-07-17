from typing import Optional
from sqlmodel import SQLModel, select
from database import engine, get_session
from models import User


def create_tables():
    SQLModel.metadata.create_all(engine)


def get_user(email: str, password: str) -> Optional[User]:
    with get_session() as session:
        statement = select(User).where(User.email == email, User.password == password)
        result = session.exec(statement).first()
        return result
