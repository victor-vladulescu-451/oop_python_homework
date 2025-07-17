from datetime import datetime
from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):

    __tablename__ = "users"

    id: int = Field(default=None, primary_key=True)
    email: str
    password: str
    created_at: datetime = Field(default_factory=datetime.now)
