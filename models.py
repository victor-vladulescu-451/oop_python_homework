from datetime import datetime
from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):

    __tablename__ = "users"

    id: int = Field(default=None, primary_key=True)
    email: str
    password: str
    created_at: datetime = Field(default_factory=datetime.now)


class SystemMetric(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.now)
    total_cpu_usage: float  # percent, e.g. 12.51
    total_ram_usage: float  # percent, e.g., 23.11


class MathRequest(SQLModel, table=True):

    __tablename__ = "math_requests"

    id: int = Field(default=None, primary_key=True)
    requested_at: datetime = Field(default_factory=datetime.now)
    user_id: int = Field(default=None, foreign_key="users.id")
    result_id: int = Field(default=None, foreign_key="math_results.id")


class MathResult(SQLModel, table=True):

    __tablename__ = "math_results"

    id: int = Field(default=None, primary_key=True)
    operation: str
    parameters: str  # JSON string of parameters
    value: str
    calculation_time: int  # in milliseconds
