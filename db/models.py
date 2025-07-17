from typing import Optional
from datetime import datetime
from sqlalchemy import String, Integer, BigInteger, Boolean, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from locales.loader import t

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user"

    id : Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    tg_id : Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    tg_username : Mapped[Optional[str]] = mapped_column(String(32))

    first_name : Mapped[str] = mapped_column(String(30))
    last_name : Mapped[str] = mapped_column(String(30))
    patronym: Mapped[Optional[str]] = mapped_column(String(30))

    phone_number : Mapped[str] = mapped_column(String(12), unique=True)
    email : Mapped[str] = mapped_column(String(120), unique=True)

    department : Mapped[Optional[str]] = mapped_column(String(40))
    position : Mapped[Optional[str]] = mapped_column(String(40))

    status : Mapped[Optional[str]] = mapped_column(String(10), default=t('service.status.pending'), nullable=False) # pending | approved | declined

    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

class Pin(Base):
    __tablename__ = "pin"

    code: Mapped[int] = mapped_column(Integer, primary_key=True)
    is_used : Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
