import enum
from datetime import date
from typing import List, Optional

from sqlalchemy import String, func, DateTime, Boolean, Enum, ForeignKey, Table, Integer, Column
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class JoinTime:
    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[date] = mapped_column(
        'created_at', DateTime, default=func.now(), nullable=True)
    updated_at: Mapped[date] = mapped_column(
        'updated_at', DateTime, default=func.now(), onupdate=func.now(), nullable=True)


class Role(enum.Enum):
    admin: str = "admin"
    moderator: str = "moderator"
    user: str = "user"


tag_for_photo = Table(
    'tag_for_photo',
    Base.metadata,
    Column('photo_id', Integer, ForeignKey('photos.id', ondelete="CASCADE")),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)


class User(JoinTime, Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    role: Mapped[Enum] = mapped_column('role', Enum(Role), default=Role.user, nullable=True)
    count_photo: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True)
    photos: Mapped["Photo"] = relationship(
        "Photo", back_populates="user", uselist=True, lazy='joined', cascade='all, delete')
    tags: Mapped[List["Tag"]] = relationship(
        secondary=tag_for_photo, back_populates="photos", lazy='joined')


class Tag(JoinTime, Base):
    __tablename__ = "tags"

    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    photos: Mapped[List["Photo"]] = relationship(
        secondary=tag_for_photo, back_populates='tags', lazy='joined')


class Photo(JoinTime, Base):
    __tablename__ = 'photos'
    url: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    cloud_id: Mapped[str] = mapped_column(String, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    user: Mapped["User"] = relationship("User", back_populates="photos", lazy='joined')
    tags: Mapped[List["Tag"]] = relationship(
        secondary=tag_for_photo, back_populates='photos', lazy='joined')


class PhotoSerialize(JoinTime, Base):
    __tablename__ = 'photo_serialize'
    natural_photo_id: Mapped[int] = mapped_column(ForeignKey('photos.id'), nullable=False)
    natural_photo = relationship("Photo", back_populates="photo_serialize")
