from datetime import datetime
from typing import Annotated
from bot.config import database_url
from sqlalchemy import func, TIMESTAMP, Integer
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, declared_attr
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine, AsyncSession
import cuid

engine = create_async_engine(url=database_url)

async_session = async_sessionmaker(engine, class_=AsyncSession)

# настройка аннотаций
str_pk = Annotated[str, mapped_column(primary_key=True, default=lambda: cuid.cuid())]
created_at = Annotated[datetime, mapped_column(server_default=func.now())]
updated_at = Annotated[datetime, mapped_column(server_default=func.now(), onupdate=datetime.now)]

class Base(DeclarativeBase, AsyncAttrs):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}s"

    id: Mapped[str_pk]
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]