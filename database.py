from sqlmodel import create_engine, Session

DATABASE_URL = "postgresql+psycopg2://postgres:VerySecurePassword123@localhost:5432/app"
engine = create_engine(DATABASE_URL, echo=False)


def get_session():
    return Session(engine)
