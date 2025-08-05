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
    total_cpu_usage: float # percent, e.g. 12.51
    total_ram_usage: float # percent, e.g., 23.11
    
