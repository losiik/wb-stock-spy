from datetime import datetime

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    DateTime,
    BigInteger,
    Integer,
    Boolean
)


class Base(DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = "product"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=True)
    url = Column(String, nullable=True)
    wb_product_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=True, default=datetime.now())


class Settings(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True)
    last_product_id = Column(Integer, ForeignKey('product.id', ondelete='CASCADE'))
    price = Column(Integer, nullable=True)
    unlimited = Column(Boolean, nullable=False)
    amount = Column(Integer, nullable=True)
