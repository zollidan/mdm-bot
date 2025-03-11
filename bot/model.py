from sqlalchemy import BigInteger, ForeignKey, Integer, UniqueConstraint, Text
from bot.database import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
    
class User(Base):
    __tablename__ = "users"
    
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str | None] = mapped_column(Text)
    first_name: Mapped[str | None] = mapped_column(Text)
    last_name: Mapped[str | None] = mapped_column(Text)

    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, username={self.username})>"

class Product(Base):
    __tablename__ = "products"


class Category(Base):
    __tablename__ = "categories"

