from typing import Optional
from sqlmodel import SQLModel, select
from database import engine, get_session
from models import MathRequest, MathResult, User


def create_tables():
    SQLModel.metadata.create_all(engine)


def get_user(email: str, password: str) -> Optional[User]:
    with get_session() as session:
        statement = select(User).where(User.email == email, User.password == password)
        result = session.exec(statement).first()
        return result


def get_math_result(operation: str, parameters: str) -> Optional[MathResult]:
    with get_session() as session:
        statement = select(MathResult).where(
            MathResult.operation == operation, MathResult.parameters == parameters
        )
        result = session.exec(statement).first()
        return result


def save_math_result(result: MathResult) -> MathResult:

    existing_result = get_math_result(result.operation, result.parameters)
    if existing_result:
        return existing_result

    with get_session() as session:
        session.add(result)
        session.commit()
        session.refresh(result)
        return result


def save_math_request(request: MathRequest) -> MathRequest:
    with get_session() as session:
        session.add(request)
        session.commit()
        session.refresh(request)
        return request
