from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import String, Integer, BigInteger, Boolean, DateTime, Enum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass

class StatusEnum(PyEnum):
    pending = 0
    accept = 1
    declined = -1


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

    # pending | accept | declined
    status : Mapped[int] = mapped_column(Integer, default=StatusEnum.pending.value, nullable=False)

    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    def __str__(self):
        return f"{self.tg_id}: {self.first_name} {self.last_name}"

class Pin(Base):
    __tablename__ = "pin"

    code: Mapped[int] = mapped_column(Integer, primary_key=True)
    is_used : Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())

class SourceTypeEnum(PyEnum):
    telegram = "telegram"
    local = "local"
    url = "url"

class Media(Base):
    __tablename__ = "media"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    file_id: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    filename: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    type : Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    tag: Mapped[str] = mapped_column(String(50), nullable=False)

    source_type: Mapped[SourceTypeEnum]

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())

    def __str__(self):
        return f"{self.filename}({self.file_id})\ntag:{self.tag}\npath:{self.path}\nsource_type:{self.source_type}"
