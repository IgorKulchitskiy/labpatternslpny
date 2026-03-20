from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from data.entities import Base

engine = create_engine("sqlite:///lab2.db")
SessionLocal = sessionmaker(bind=engine)


def init_db():
    Base.metadata.create_all(engine)