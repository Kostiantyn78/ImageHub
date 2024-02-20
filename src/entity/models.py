import enum
from datetime import date
from typing import List, Optional

from sqlalchemy import String, func, DateTime, Boolean, Enum, ForeignKey, Table, Integer, Column
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Role(enum.Enum):
    admin: str = "admin"
    moderator: str = "moderator"
    user: str = "user"


class JoinTime:
    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[date] = mapped_column(
        'created_at', DateTime, default=func.now(), nullable=True)
    updated_at: Mapped[date] = mapped_column(
        'updated_at', DateTime, default=func.now(), onupdate=func.now(), nullable=True)


tag_for_photo = Table(
    'tag_for_photo',
    Base.metadata,
    Column('images_id', Integer, ForeignKey('images.id', ondelete="CASCADE")),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)


class User(JoinTime, Base):
    """

       Relationships:
       - One-to-Many relationship with Photo model via `photos` attribute.

    """

    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    role: Mapped[Enum] = mapped_column('role', Enum(Role), default=Role.user, nullable=True)
    count_photo: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    photos: Mapped[List["Image"]] = relationship(
        "Image", back_populates="user", uselist=True, lazy='joined', cascade='all, delete')


class Tag(JoinTime, Base):
    """

       Relationships:
       - Many-to-Many relationship with Photo model via `images` attribute.

    """

    __tablename__ = "tags"

    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    images: Mapped[List["Image"]] = relationship(
        secondary=tag_for_photo, back_populates='tags', lazy='joined')


class Image(JoinTime, Base):
    """

       Relationships:
       - Many-to-One relationship with User model via `user` attribute.
       - Many-to-Many relationship with Tag model via `tags` attribute.
       - One-to-Many relationship with PhotoSerialize model via `initial_photo` attribute.

    """

    __tablename__ = 'images'

    url: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    user: Mapped["User"] = relationship("User", back_populates="photos", lazy='joined')
    tags: Mapped[List["Tag"]] = relationship(
        secondary=tag_for_photo, back_populates='images', lazy='joined', uselist=True, cascade='all, delete')

    transform: Mapped[List["Transform"]] = relationship("Transform",
                                                        back_populates="initial_photo", lazy='joined')


class Transform(JoinTime, Base):
    """

        Relationships:
        - Many-to-One relationship with Photo model via `initial_photo` attribute.

    """

    __tablename__ = 'transform'
    natural_photo_id: Mapped[int] = mapped_column(ForeignKey('images.id'), nullable=False)
    image_url: Mapped[str] = mapped_column(String(255), nullable=False)
    cloudinary_public_id: Mapped[str] = mapped_column(String, nullable=False)  # TODO: Cloudinary
    qr_code_url: Mapped[str] = mapped_column(String(255), nullable=True)
    qr_code_public_id: Mapped[str] = mapped_column(String, nullable=True)  # TODO: Cloudinary
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    initial_photo = relationship("Image", back_populates="transform")
