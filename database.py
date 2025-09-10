# MARK: db


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
from config import settings

url = f"postgresql+asyncpg ://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"

engine = create_engine(url, echo=True)

Session = sessionmaker(engine)


def create_tables():
    Base.metadata.create_all(engine)
