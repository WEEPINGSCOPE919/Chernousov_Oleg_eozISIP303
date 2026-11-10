from sqlalchemy import ForeignKey, String, Text, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base


class User(Base):
    __tablename__ = "Users"
    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False)

    __table_args__ = (
        CheckConstraint(
            "role IN ('admin','operator','executor','applicant')",
            name="ck_user_role",
        ),
    )


class Category(Base):
    __tablename__ = "Categories"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)


class Status(Base):
    __tablename__ = "Statuses"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)


class Request(Base):
    __tablename__ = "Requests"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(String, nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("Categories.id"))
    status_id: Mapped[int] = mapped_column(ForeignKey("Statuses.id"))
    applicant_id: Mapped[int] = mapped_column(ForeignKey("Users.id"))
    executor_id: Mapped[int | None] = mapped_column(ForeignKey("Users.id"), nullable=True)

    category = relationship("Category")
    status = relationship("Status")
    applicant = relationship("User", foreign_keys=[applicant_id])
    executor = relationship("User", foreign_keys=[executor_id])
    comments = relationship("Comment", back_populates="request", cascade="all, delete-orphan")


class Comment(Base):
    __tablename__ = "Comments"
    id: Mapped[int] = mapped_column(primary_key=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("Requests.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("Users.id"))
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(String, nullable=False)

    request = relationship("Request", back_populates="comments")
    user = relationship("User")